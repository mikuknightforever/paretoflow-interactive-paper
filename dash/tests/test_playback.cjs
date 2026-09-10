const assert = require('node:assert/strict');
const fs = require('node:fs');
const noUpdate = Symbol('no update');
globalThis.dash_clientside = {no_update: noUpdate, callback_context: {triggered: []}};
const {transition, frame, control} = require('../assets/playback.js');
const records = JSON.parse(fs.readFileSync(0, 'utf8'));

// Start at the update window, pause on the current frame, ignore queued ticks,
// resume without a jump, and stop exactly once at the final recorded frame.
assert.deepEqual(transition('evo-play', true, 160, noUpdate), [false, '❚❚ Pause', 124]);
assert.equal(transition('evo-play', true, 62, noUpdate)[2],124);
assert.deepEqual(transition('evo-clock', false, 140, noUpdate), [false, '❚❚ Pause', 141]);
assert.deepEqual(transition('evo-play', false, 141, noUpdate), [true, '▶ Resume', noUpdate]);
for (let tick=0; tick<10; tick++) {
    assert.deepEqual(transition('evo-clock', true, 141, noUpdate), [noUpdate,noUpdate,noUpdate]);
}
assert.deepEqual(transition('evo-play', true, 141, noUpdate), [false, '❚❚ Pause', 141]);
assert.deepEqual(transition('evo-clock', false, 159, noUpdate), [true, '▶ Replay updates', 160]);
assert.deepEqual(transition('evo-clock', true, 160, noUpdate), [noUpdate,noUpdate,noUpdate]);

// Dash can batch events: a pause must take priority over the concurrent tick.
globalThis.dash_clientside.callback_context.triggered = [
    {prop_id:'evo-clock.n_intervals'}, {prop_id:'evo-play.n_clicks'}
];
assert.deepEqual(control(2,10,false,140),[true,'▶ Resume',noUpdate]);

const figure = {data:[{name:'front',x:[0,1],y:[1,0]}, {name:'archive',x:[],y:[]}],layout:{uirevision:'evolution'}};
for (let step=0; step<records.frames.length; step++) {
    const [next, detail] = frame(step,records,figure);
    assert.deepEqual(next.data[1].x,records.frames[step].x);
    assert.deepEqual(next.data[1].y,records.frames[step].y);
    assert.equal(next.data[0],figure.data[0]);
    assert.equal(next.layout,figure.layout);
    assert.ok(detail.includes(records.coverage[step].toFixed(3)));
    assert.ok(detail.includes(records.times[step].toFixed(3)));
    assert.deepEqual(figure.data[1].x,[]); // no mutation of prior frame
}
assert.notDeepEqual(frame(128,records,figure)[0].data[1].y,frame(160,records,figure)[0].data[1].y);
console.log('Playback state transitions and all 161 recorded frames passed');
