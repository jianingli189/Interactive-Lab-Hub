const assert = require('node:assert/strict');
const {recipeReducer:r,initialRecipeState,activeMicro} = require(process.argv[2]+'/state/recipeState.js');
let t=10000;
let s=r(initialRecipeState(),{type:'START_COOKING',now:t});
const act=a=>s=r(s,{now:t+=2000,...a});
const confirm=()=>act({type:'CONFIRM',source:'gesture'});
const reading=present=>act({type:'TOOL_READING',microId:activeMicro(s).id,present});
const next=()=>act({type:'NAV',dir:1});
next(); assert.equal(activeMicro(s).id,'chop-scallion');
reading(false);confirm();assert.equal(s.micro['chop-scallion'].status,'active','off-station alone is not a pickup');
reading(true);reading(false);assert.equal(s.micro['chop-scallion'].toolStage,'using');
confirm();assert.equal(s.micro['chop-scallion'].status,'done');assert.equal(activeMicro(s).id,'chop-scallion');
const stamp=s.lastCompleted.at;confirm();assert.equal(s.lastCompleted.at,stamp,'duplicate nod does not replay completion');
next();assert.equal(activeMicro(s).id,'chop-scallion','return required');
reading(true);next();assert.equal(activeMicro(s).id,'add-egg');
act({type:'UNDO'});assert.equal(activeMicro(s).id,'chop-scallion');assert.equal(s.micro['chop-scallion'].status,'done');
act({type:'UNDO'});assert.equal(s.micro['chop-scallion'].status,'active','undo removes completion');
// Complete the full recipe, verifying every navigation boundary.
let iterations=0;
while(!s.finishedAt && iterations++<100) {
 const m=activeMicro(s);
 if (s.micro[m.id].status!=='done') {
  reading(true);reading(false);confirm();
  if(s.micro[m.id].status!=='done') confirm(); // deliberate early timer confirmation
 }
 reading(true);next();
}
assert.ok(s.finishedAt,'entire recipe reaches finale');assert.ok(iterations<100);
assert.equal(s.micro['spoon-return'],undefined);
// Duration recognition only after pickup, return prompt without implicit completion.
s=r(initialRecipeState(),{type:'START_COOKING',now:t});
s={...s,active:{step:3,micro:0},viewedStep:3,micro:{...s.micro,'whisk-batter':{...s.micro['whisk-batter'],status:'active'}}};
act({type:'MOTION',classifier:'WHISKING',signal:'active',intensity:.5});assert.equal(s.micro['whisk-batter'].motion.activeSince,null);
reading(true);reading(false);act({type:'MOTION',classifier:'WHISKING',signal:'active',intensity:.5});t+=31000;act({type:'MOTION',classifier:'WHISKING',signal:'sample',intensity:.5});
assert.equal(s.micro['whisk-batter'].toolStage,'return');assert.equal(s.micro['whisk-batter'].status,'active');
reading(true);confirm();next();assert.equal(activeMicro(s).id,'add-scallions');
console.log('Recipe flow passed: pickup, completion, return, next, undo, full recipe, stirring duration.');
