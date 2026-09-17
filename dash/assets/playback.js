/* Local playback controls; the evolution panel also maps saved frames locally. */
(function (root) {
    "use strict";
    const api = root.dash_clientside = root.dash_clientside || {};

    const evolution = {
        button: "evo-play", clock: "evo-clock", increment: 1, skipEarly: true,
        pausedLabel: "▶ Resume", endedLabel: "▶ Replay updates"
    };
    const explorer = {
        button: "play", clock: "clock", increment: 2, skipEarly: false,
        pausedLabel: "▶ Replay", endedLabel: "▶ Replay"
    };

    function transition(trigger, disabled, step, noUpdate, config = evolution) {
        step = Math.max(0, Math.min(160, Math.round(Number(step))));
        if (trigger === config.button) {
            if (!disabled) return [true, config.pausedLabel, noUpdate];
            const start = step >= 160 || (config.skipEarly && step < 124) ? 124 : step;
            return [false, "❚❚ Pause", start];
        }
        // A queued interval must never undo a pause or move its saved frame.
        if (disabled || trigger !== config.clock) return [noUpdate, noUpdate, noUpdate];
        const next = Math.min(160, step + config.increment);
        return [next === 160, next === 160 ? config.endedLabel : "❚❚ Pause", next];
    }

    function makeControl(config) {
        return function (_clicks, _ticks, disabled, step) {
            const changed = api.callback_context.triggered || [];
            // A click wins regardless of the ordering of batched interval events.
            const trigger = changed.some(item => item.prop_id === config.button + ".n_clicks")
                ? config.button
                : changed.some(item => item.prop_id === config.clock + ".n_intervals")
                    ? config.clock : "";
            return transition(trigger, disabled, step, api.no_update, config);
        };
    }

    function frame(step, records, figure) {
        if (!records || !figure || !Number.isInteger(step) || !records.frames[step]) {
            return [api.no_update, api.no_update];
        }
        const saved = records.frames[step];
        const traces = figure.data.map((trace, index) => index === 1
            ? Object.assign({}, trace, {x: saved.x, y: saved.y}) : trace);
        const t = records.times[step];
        const stage = t < 0.8 ? "Archive unchanged during flow transport" : "Proposal and archive updates";
        const detail = `t = ${t.toFixed(3)} · evaluated hypervolume ${records.coverage[step].toFixed(3)} · ${stage}`;
        return [Object.assign({}, figure, {data: traces}), detail];
    }

    api.paretoPlayback = {
        control: makeControl(evolution),
        explorerControl: makeControl(explorer),
        frame: frame
    };
    // Exercise the production reducer and frame mapper in Node regression tests.
    if (typeof module !== "undefined" && module.exports) {
        module.exports = {
            transition, frame, control: api.paretoPlayback.control,
            explorerControl: api.paretoPlayback.explorerControl
        };
    }
})(typeof window === "undefined" ? globalThis : window);
