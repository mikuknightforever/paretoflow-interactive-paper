/* Replay saved observations locally. No requests or interpolated coordinates. */
(function (root) {
    "use strict";
    const api = root.dash_clientside = root.dash_clientside || {};

    function transition(trigger, disabled, step, noUpdate) {
        step = Math.max(0, Math.min(160, Math.round(Number(step))));
        if (trigger === "evo-play") {
            if (!disabled) return [true, "▶ Resume", noUpdate];
            const start = step >= 160 || step < 124 ? 124 : step;
            return [false, "❚❚ Pause", start];
        }
        // A queued interval must never undo a pause or move its saved frame.
        if (disabled || trigger !== "evo-clock") return [noUpdate, noUpdate, noUpdate];
        const next = Math.min(160, step + 1);
        return [next === 160, next === 160 ? "▶ Replay updates" : "❚❚ Pause", next];
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
        control: function (_clicks, _ticks, disabled, step) {
            const changed = api.callback_context.triggered || [];
            // A click wins if Dash batches it with an interval event.
            const trigger = changed.some(item => item.prop_id === "evo-play.n_clicks")
                ? "evo-play" : (changed[0] ? changed[0].prop_id.split(".")[0] : "");
            return transition(trigger, disabled, step, api.no_update);
        },
        frame: frame
    };
    // Exercise the production reducer and frame mapper in Node regression tests.
    if (typeof module !== "undefined" && module.exports) {
        module.exports = {transition, frame, control: api.paretoPlayback.control};
    }
})(typeof window === "undefined" ? globalThis : window);
