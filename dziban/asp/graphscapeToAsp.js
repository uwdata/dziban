'use strict';

const args = process.argv;

if (args.length != 4) {
  throw new Error('Usage: node graphscapeToAsp.js <path_to_graphscape_weight_def> <output_dir>');
}

const def_path = args[2];

const def = require(def_path);

const weights = [];
for (const key in def.DEFAULT_EDIT_OPS) {
  const opGroup = def.DEFAULT_EDIT_OPS[key];

  for (const name in opGroup) {
    const aspName = `edit_${name.toLowerCase()}_weight`;
    const cost = Math.round(opGroup[name].cost * 100);  // need integers

    const aspWeight = `#const ${aspName} = ${cost}.`
    weights.push(aspWeight);
  }
}

let weightsOutput = `%% FILE GENERATED BY graphscapeToAsp.js, DO NOT MODIFY %%\n`;
weightsOutput += weights.join('\n');

const fs = require('fs');

const output_dir = args[3];

fs.writeFileSync(`${output_dir}/graphscape.lp`, weightsOutput);

const rules = [];
const markGroup = def.DEFAULT_EDIT_OPS['markEditOps'];

rules.push(`comparable(V1,V2) :- view(V1), base(V1), view(V2), V1 != V2.`)

rules.push(`% MARK EDITS`);
for (let name in markGroup) {
  name = name.toLowerCase();
  const marks = name.split('_');
  rules.push(`compare(edit_${name},V1,V2,${marks[0]},${marks[1]}) :- comparable(V1,V2), mark(V1,${marks[0]}), mark(V2,${marks[1]}).`);
  rules.push(`compare(edit_${name},V1,V2,${marks[1]},${marks[0]}) :- comparable(V1,V2), mark(V1,${marks[1]}), mark(V2,${marks[0]}).`)
}

rules.push('\n');

const encodingGroup = def.DEFAULT_EDIT_OPS['encodingEditOps'];
rules.push(`% ENCODING EDITS`);
for (let name in encodingGroup) {
  name = name.toLowerCase();
  const tokens = name.split('_');
  const action = tokens[0];
  const props = tokens.slice(1);

  if (action === 'add') {
    if (props.length === 1) {
      const head = `compare(edit_${name},V1,V2,E2,F2,add,none,${props[0]})`;
      const add = `comparable(V1,V2), channel(V2,E2,${props[0]}), field(V2,E2,F2), not channel(V1,_,${props[0]})`;
      const duplicateCount = `${name}_count`;
      const duplicateMove = `not compare(_,V1,V2,_,E2,move,_,${props[0]})`;  // don't count if field was moved
      const duplicateRule = `not compare(edit_${duplicateCount},V1,V2,E2,count,add,none,${props[0]})`;  // don't double dip count case
      rules.push(`${head} :- ${duplicateRule}, ${duplicateMove}, ${add}.`)
    
    } else if (props.length === 2) {
      if (props[1] === 'count') {
        const head = `compare(edit_${name},V1,V2,E2,count,add,none,${props[0]})`;
        const duplicateMove = `not compare(_,V1,V2,_,E2,move,_,${props[0]})`;  // don't count if field was moved
        const add = `comparable(V1,V2), channel(V2,E2,${props[0]}), aggregate(V2,E2,count), not channel(V1,_,${props[0]})`;

        rules.push(`${head} :- ${duplicateMove}, ${add}.`)
      }
    }
  } else if (action === 'remove') {
    if (props.length === 1) {
      const head = `compare(edit_${name},V1,V2,E1,F1,remove,${props[0]},none)`;
      const remove = `comparable(V1,V2), channel(V1,E1,${props[0]}), field(V1,E1,F1), not channel(V2,_,${props[0]})`

      const duplicateCount = `${name}_count`;
      const duplicateMove = `not compare(_,V1,V2,E1,_,move,${props[0]},_)`;  // don't count if field was moved
      const duplicateRule = `not compare(edit_${duplicateCount},V1,V2,E1,count,remove,${props[0]},none)`;  // don't double dip count case
      rules.push(`${head} :- ${duplicateRule}, ${duplicateMove}, ${remove}.`)
    } else if (props.length === 2) {
      if (props[1] === 'count') {
        const head = `compare(edit_${name},V1,V2,E1,count,remove,${props[0]},none)`;
        const remove = `comparable(V1,V2), channel(V1,E1,${props[0]}), aggregate(V1,E1,count), not channel(V2,_,${props[0]})`;
        const duplicateMove = `not compare(_,V1,V2,E1,_,move,${props[0]},_)`;  // don't count if field was moved

        rules.push(`${head} :- ${duplicateMove}, ${remove}.`)
      }
    }
  } else if (action === 'move') {
    const head = `compare(edit_${name},V1,V2,E1A,E2A,move,${props[0]},${props[1]})`;
    if (props.length === 2) {
      // field from V1 changed channel in V2, but did not swap
      const move = `comparable(V1,V2), field(V1,E1A,F), field(V2,E2A,F), channel(V1,E1A,${props[0]}), channel(V2,E2A,${props[1]})`;

      // hard code for now since swaps are not exhaustive
      if (props === ['x', 'y'] || props === ['row', 'column']) {
        const duplicateRule = `not compare(_,V1,V2,E1A,E2A,swap,${props[0]},${props[1]})`;
        rules.push(`${head} :- ${duplicateRule}, ${move}.`);
      } else {
        rules.push(`${head} :- ${move}.`);
      }
    }
  } else if (action === 'swap') {
    const head = `compare(edit_${name},V1,V2,E1A,E2A,swap,${props[0]},${props[1]})`;
    if (props.length === 2) {
      // field from V1 now in V2 channel, which had its field in the same V1 channel.
      const swap = `comparable(V1,V2), channel(V1,E1A,${props[0]}), channel(V1,E1B,${props[1]}), channel(V2,E2A,${props[0]}), channel(V2,E2B,${props[1]}), field(V1,E1A,FA), field(V2,E2B,FA), field(V1,E1B,FB), field(V2,E2A,FB), E2A > E2B, E1A > E1B`;
      rules.push(`${head} :- ${swap}.`);
    }
  } else if (action === 'modify') {
    // field of a channel changed
    if (props.length === 1) {
      const head = `compare(edit_${name},V1,V2,E1,F2,modify,${props[0]},none)`;

      // don't double dip count, move, or swap cases
      const modify = `comparable(V1,V2), channel(V1,E1,${props[0]}), channel(V2,E2,${props[0]}), field(V2,E2,F2), not field(V1,_,F2)`;

      const duplicateModifyAddCount = `${name}_add_count`;
      const duplicateModifyRemoveCount = `${name}_remove_count`;
      const duplicateRule = `not compare(edit_${duplicateModifyAddCount},V1,V2,E1,count,modify,${props[0]},none), not compare(edit_${duplicateModifyRemoveCount},V1,V2,E1,count,modify,${props[0]},none)`;
      rules.push(`${head} :- ${duplicateRule}, ${modify}.`)
    } else if (props.length === 3) {
      const head = `compare(edit_${name},V1,V2,E1,count,modify,${props[0]},none)`;
      if (props[1] === 'add' && props[2] === 'count') {
        const modify = `comparable(V1,V2), channel(V1,E1,${props[0]}), channel(V2,E2,${props[0]}), not aggregate(V1,E1,count), aggregate(V2,E2,count)`;
        rules.push(`${head} :- ${modify}.`)
      } else if (props[1] === 'remove' && props[2] === 'count') {
        const modify = `comparable(V1,V2), channel(V1,E1,${props[0]}), channel(V2,E2,${props[0]}), aggregate(V1,E1,count), not aggregate(V2,E2,count)`;

        rules.push(`${head} :- ${modify}.`)
      }
    }
  } 
}

// HAND WRITTEN TRANSFORM EDITS
rules.push('\n')
rules.push(`compare(edit_scale,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), log(V1,E1), not log(V2,E2).
compare(edit_scale,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), not log(V1,E1), log(V2,E2).
compare(edit_scale,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), zero(V1,E1), not zero(V2,E2).
compare(edit_scale,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), not zero(V1,E1), zero(V2,E2).

compare(edit_bin,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), bin(V1,E1,_), not bin(V2,E2,_).
compare(edit_bin,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), not bin(V1,E1,_), bin(V2,E2,_).

compare(edit_aggregate,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), aggregate(V1,E1,A1), aggregate(V2,E2,A2), A1 != A2.
compare(edit_aggregate,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), aggregate(V1,E1,_), not aggregate(V2,E2,_), not compare(_,V1,V2,E2,count,_,_,_).
compare(edit_aggregate,V1,V2,E1,E2) :- comparable(V1,V2), field(V1,E1,F), field(V2,E2,F), not aggregate(V1,E1,_), aggregate(V2,E2,_), not compare(_,V1,V2,E2,count,_,_,_).

compare(NAME,V1,V2,A,B) :- compare(NAME,V1,V2,A,B,_,_,_).
`)

let rulesOutput = `%% FILE GENERATED BY graphscapeToAsp.js, DO NOT MODIFY %%\n`;
rulesOutput += rules.join('\n');

fs.writeFileSync(`${output_dir}/compare.lp`, rulesOutput);