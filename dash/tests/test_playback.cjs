const assert = require('node:assert/strict');
const fs = require('node:fs');
const noUpdate = Symbol('no update');
globalThis.dash_clientside = {no_update: noUpdate, callback_context: {triggered: []}};
const {transition, frame, control, explorerControl} = require('../assets/playback.js');
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

function invoke(handler, triggers, disabled, step, clicks=2, ticks=10) {
    globalThis.dash_clientside.callback_context.triggered = triggers.map(prop_id => ({prop_id}));
    return handler(clicks, ticks, disabled, step);
}

const unchanged = [noUpdate, noUpdate, noUpdate];
const controllers = [
    {name:'evolution', handler:control, play:'evo-play.n_clicks', clock:'evo-clock.n_intervals',
        otherPlay:'play.n_clicks', earlyStart:124, stride:1, pausedLabel:'▶ Resume', endedLabel:'▶ Replay updates'},
    {name:'explorer', handler:explorerControl, play:'play.n_clicks', clock:'clock.n_intervals',
        otherPlay:'evo-play.n_clicks', earlyStart:62, stride:2, pausedLabel:'▶ Replay', endedLabel:'▶ Replay'}
];

for (const config of controllers) {
    const {name, handler, play, clock, otherPlay, earlyStart, stride, pausedLabel, endedLabel} = config;
    assert.equal(typeof handler, 'function', `${name} must expose its production controller`);
    assert.deepEqual(invoke(handler, [play], true, 160), [false, '❚❚ Pause', 124], `${name}: replay from end`);
    assert.deepEqual(invoke(handler, [play], true, 62), [false, '❚❚ Pause', earlyStart], `${name}: preserve early-start policy`);
    assert.deepEqual(invoke(handler, [play], true, 140), [false, '❚❚ Pause', 140], `${name}: resume in place`);
    assert.deepEqual(invoke(handler, [clock], false, 140), [false, '❚❚ Pause', 140+stride], `${name}: preserve stride`);

    // A pause wins even if Dash reports the clock first in the same batch.
    for (const triggers of [[clock, play], [play, clock]]) {
        assert.deepEqual(invoke(handler, triggers, false, 140), [true, pausedLabel, noUpdate], `${name}: batched pause priority`);
        assert.deepEqual(invoke(handler, triggers, true, 140), [false, '❚❚ Pause', 140], `${name}: batched resume must not advance`);
    }
    for (let tick=0; tick<10; tick++) {
        assert.deepEqual(invoke(handler, [clock], true, 140, 2, tick), unchanged, `${name}: ignore ticks after pause`);
    }
    assert.deepEqual(invoke(handler, [clock], false, 159), [true, endedLabel, 160], `${name}: clamp last step`);
    assert.deepEqual(invoke(handler, [clock], true, 160), unchanged, `${name}: remain stopped at end`);
    for (const triggers of [[], ['unrelated.value'], [otherPlay]]) {
        assert.deepEqual(invoke(handler, triggers, false, 140), unchanged, `${name}: unrelated trigger`);
    }

    // Apply real outputs back into the next invocation, including no_update,
    // so rapid pause/resume cycles cannot lose the current frame or restart.
    let state = [false, '❚❚ Pause', 140];
    let clicks = 1;
    const dispatch = triggers => {
        const next = invoke(handler, triggers, state[0], state[2], clicks, 50);
        state = next.map((value, i) => value === noUpdate ? state[i] : value);
    };
    for (let cycle=0; cycle<3; cycle++) {
        clicks++;
        dispatch([play]);
        assert.deepEqual(state, [true, pausedLabel, 140], `${name}: rapid pause`);
        dispatch([clock]);
        assert.deepEqual(state, [true, pausedLabel, 140], `${name}: queued tick leaves paused state intact`);
        clicks++;
        dispatch([play]);
        assert.deepEqual(state, [false, '❚❚ Pause', 140], `${name}: rapid resume`);
    }
    dispatch([clock]);
    assert.deepEqual(state, [false, '❚❚ Pause', 140+stride], `${name}: resume advances only on next tick`);
}

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
console.log('Both playback controllers and all 161 recorded frames passed');
