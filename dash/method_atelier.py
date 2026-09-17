"""A compact visual walkthrough of actual ParetoFlow sampling decisions."""
import math
from pathlib import Path
from urllib.parse import urlencode

import plotly.graph_objects as go
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from flask import redirect

from process_view import load_trace, select_record


INK = '#142b42'
TEAL = '#078783'
AMBER = '#d18b27'
VIOLET = '#7861ae'
MUTED = '#617486'
GRAY = '#bdcbd4'
COLORS = (TEAL, VIOLET, AMBER)
STAGES = ('Generate', 'Pool', 'Filter', 'Select', 'Archive')
CONFIG = {'displayModeBar': False, 'responsive': True}


def decision_steps(trace):
    """Compact lookup of records that actually contain a candidate decision."""
    return {
        mode: {
            str(direction): [frame['step'] for frame in run['frames']
                             if any(record['id'] == direction and record['candidates']
                                    for record in frame['directions'])]
            for direction in trace['directions']
        }
        for mode, run in trace['modes'].items()
    }


def _figure(height=240):
    fig = go.Figure()
    fig.update_layout(template='plotly_white', height=height,
                      margin=dict(l=42, r=12, t=18, b=38),
                      font=dict(family='Arial, sans-serif', size=11, color=INK),
                      paper_bgcolor='white', plot_bgcolor='white',
                      showlegend=False, dragmode=False, transition=dict(duration=0))
    fig.update_xaxes(fixedrange=True, gridcolor='#edf2f5', zeroline=False)
    fig.update_yaxes(fixedrange=True, gridcolor='#edf2f5', zeroline=False)
    return fig


def _angle_invalid(record):
    return (record['half_angle_deg'] is None
            or any(item['angle_deg'] is None for item in record['candidates']))


def _status(candidate, record):
    if candidate['fallback']:
        return ('numerical safeguard' if candidate['angle_deg'] is None or record['half_angle_deg'] is None
                else 'outside-cone fallback')
    return 'passes angle test' if candidate['admitted'] else 'excluded by angle test'


def _source_colors(record):
    return {source: COLORS[index % len(COLORS)] for index, source in enumerate(record['neighbors'])}


def _visible(candidate, record, stage):
    return stage > 0 or candidate['source_direction'] == record['id']


def _candidate_style(candidate, record, stage):
    if not _visible(candidate, record, stage):
        return GRAY, .16, 'circle', 16
    color = _source_colors(record)[candidate['source_direction']]
    if stage >= 2 and not candidate['admitted']:
        return GRAY, .43, 'x', 12
    if stage >= 3 and candidate['selected']:
        return INK, 1, 'star', 23
    return color, .50 if stage >= 3 else 1, 'circle', 17


def _candidate_diagram(record, stage, inspected):
    fig = _figure()
    sources = record['neighbors']
    colors = _source_colors(record)
    rows = {item['id']: 1 - (index + .5) / len(record['candidates']) for index, item in enumerate(record['candidates'])}
    for source in sources:
        children = [item for item in record['candidates'] if item['source_direction'] == source]
        y = sum(rows[item['id']] for item in children) / len(children)
        active = stage > 0 or source == record['id']
        for item in children:
            color, opacity, symbol, size = _candidate_style(item, record, stage)
            fig.add_trace(go.Scatter(x=[.16, .61], y=[y, rows[item['id']]], mode='lines',
                                    line=dict(color=color, width=2.5 if stage >= 3 and item['selected'] else 1.2),
                                    opacity=opacity * .6, hoverinfo='skip'))
        fig.add_trace(go.Scatter(x=[.09], y=[y], mode='markers+text', text=[str(source)],
                                textposition='middle center', textfont=dict(size=11, color='white'),
                                marker=dict(size=36, color=colors[source] if active else GRAY),
                                opacity=1 if active else .4, hovertemplate=f'Source direction {source}<extra></extra>'))
    for item in record['candidates']:
        color, opacity, symbol, size = _candidate_style(item, record, stage)
        if not _visible(item, record, stage):
            # Preserve the schematic layout without exposing an as-yet unpooled
            # candidate through its label, hover or click payload.
            fig.add_trace(go.Scatter(x=[.64], y=[rows[item['id']]], mode='markers',
                                    marker=dict(size=size, color=color), opacity=opacity, hoverinfo='skip'))
            continue
        fig.add_trace(go.Scatter(x=[.64], y=[rows[item['id']]], mode='markers+text',
                                text=[f"C{item['id']}"], textposition='middle right',
                                textfont=dict(size=10, color=MUTED if opacity < .5 else INK),
                                marker=dict(size=size, color=color, symbol=symbol), opacity=opacity,
                                customdata=[item['id']],
                                hovertemplate=f"Candidate C{item['id']}<br>Source {item['source_direction']} · offspring {item['offspring']}<extra></extra>"))
        if item['id'] == inspected and _visible(item, record, stage):
            fig.add_trace(go.Scatter(x=[.64], y=[rows[item['id']]], mode='markers',
                                    marker=dict(size=27, symbol='circle-open', color=AMBER, line=dict(width=2)),
                                    customdata=[item['id']], hoverinfo='skip'))
    chosen = next(item for item in record['candidates'] if item['selected'])
    if stage == 4:
        if record['updated']:
            fig.add_annotation(x=1.04, y=.5, ax=.71, ay=rows[chosen['id']], xref='x', yref='y',
                               axref='x', ayref='y', showarrow=True, arrowcolor=TEAL, arrowwidth=2, arrowhead=3, text='')
        fig.add_trace(go.Scatter(x=[1.15], y=[.5], mode='markers+text',
                                marker=dict(size=41, symbol='square', color=TEAL if record['updated'] else '#e4ebf0'),
                                text=['↑' if record['updated'] else '='], textfont=dict(size=23, color='white' if record['updated'] else MUTED),
                                hovertemplate='Saved clean design '+('updated' if record['updated'] else 'retained')+'<extra></extra>'))
        fig.add_annotation(x=1.15, y=.29, showarrow=False, text='Updated' if record['updated'] else 'Retained', font=dict(size=10, color=INK))
    else:
        fig.add_trace(go.Scatter(x=[1.15], y=[.5], mode='markers', marker=dict(size=35, symbol='square-open', color='#dce5ec'), hoverinfo='skip'))
    for x, label in ((.09, 'Source stream'), (.65, 'Offspring'), (1.15, 'Archive')):
        fig.add_annotation(x=x, y=1.07, text=label, showarrow=False, font=dict(size=10, color=MUTED))
    fig.update_xaxes(visible=False, range=[-.13, 1.38])
    fig.update_yaxes(visible=False, range=[-.03, 1.16])
    fig.update_layout(margin=dict(l=4, r=4, t=10, b=4))
    return fig


def _objective_view(record, stage, inspected):
    fig = _figure()
    for item in record['candidates']:
        if not _visible(item, record, stage):
            continue
        color, opacity, symbol, size = _candidate_style(item, record, stage)
        x, y = item['predicted']
        fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers+text', text=[f"C{item['id']}"],
                                textposition='top center', textfont=dict(size=9, color=MUTED),
                                marker=dict(size=size * .64, color=color, symbol=symbol), opacity=opacity,
                                customdata=[item['id']],
                                hovertemplate=f"C{item['id']} · source {item['source_direction']}<br>Predicted f₁ %{{x:.4f}}<br>Predicted f₂ %{{y:.4f}}<extra></extra>"))
        if item['id'] == inspected and _visible(item, record, stage):
            fig.add_trace(go.Scatter(x=[x], y=[y], mode='markers', marker=dict(size=21, color=AMBER, symbol='circle-open', line=dict(width=2)),
                                    customdata=[item['id']], hoverinfo='skip'))
    for index, axis in ((0, 'x'), (1, 'y')):
        values = [item['predicted'][index] for item in record['candidates']]
        pad = max((max(values) - min(values)) * .25, .0003)
        fig.update_layout(**{axis+'axis': dict(range=[min(values) - pad, max(values) + pad],
                                              title=f'Predicted f{index+1} ↓', fixedrange=True,
                                              tickformat='.3f', nticks=4)})
    return fig


def _profile(record, candidate=None, noisy=False, height=95, show_after=True):
    fig = _figure(height)
    dims = list(range(1, 31))
    before, after = ('state_before', 'state_after') if noisy else ('archive_before', 'archive_after')
    for field, name, color, dash in ((before, 'Before', GRAY, 'dot'), (after, 'After', TEAL, 'solid')):
        if field == after and not show_after:
            continue
        fig.add_trace(go.Scatter(x=dims, y=record[field], mode='lines', name=name,
                                line=dict(color=color, width=2, dash=dash),
                                hovertemplate='x%{x} = %{y:.4f}<extra>%{fullData.name}</extra>'))
    if candidate:
        fig.add_trace(go.Scatter(x=dims, y=candidate['state' if noisy else 'design'], mode='lines',
                                line=dict(color=AMBER, width=1.7, dash='dash'), name=f"C{candidate['id']}",
                                hovertemplate='x%{x} = %{y:.4f}<extra>%{fullData.name}</extra>'))
    fig.update_xaxes(range=[.5, 30.5], dtick=5, title=None)
    fig.update_yaxes(title=None, nticks=3, range=None if noisy else [-.04, 1.04])
    fig.update_layout(margin=dict(l=30, r=8, t=5, b=23))
    return fig


def method_scene(trace, mode='guided', step=140, direction=300, stage=0, candidate_id=None):
    """Render one recorded decision; candidate identity is local to this record."""
    # An unavailable phase has no selected radio button. During a record change
    # the scene may arrive before the browser resets it to Generate.
    stage = 0 if stage is None else int(stage)
    if stage not in range(5):
        raise ValueError('Unknown method stage')
    frame, record = select_record(trace, mode, step, direction)
    candidates = record['candidates']
    candidate = next((item for item in candidates if item['id'] == candidate_id), None)
    if candidate is None and candidates:
        candidate = next(item for item in candidates if item['source_direction'] == record['id'])
    inspected = candidate['id'] if candidate else None
    chosen = next((item for item in candidates if item['selected']), None)
    admitted = sum(item['admitted'] for item in candidates)
    own_count = sum(item['source_direction'] == record['id'] for item in candidates)
    score_delta = record['archive_score_after'] - record['archive_score_before']
    descriptions = [
        f"Direction {direction} generates {own_count} noisy offspring. Their predicted clean endpoints are shown at right.",
        f"{len(record['neighbors'])} neighboring streams contribute {len(candidates)} proposals. Follow each source color into the shared pool.",
        f"The recorded filter keeps {admitted} of {len(candidates)} proposals. Crosses mark exclusions; only admitted proposals can win.",
        (f"C{chosen['id']} from direction {chosen['source_direction']} has the best admitted score ({chosen['weighted_score']:.5f}). Its noisy state becomes the next stream state." if chosen else ''),
        (f"The selected clean endpoint improves the archive score by {score_delta:.5f}; the saved design is replaced." if record['updated'] else 'The selected state continues sampling, but its clean endpoint does not improve the archive. The saved design stays unchanged.'),
    ]
    if candidates:
        diagram = _candidate_diagram(record, stage, inspected)
        objective = _objective_view(record, stage, inspected)
        description = descriptions[stage]
        left_title, right_title = 'Where proposals come from', 'The same candidates in objective space'
        invalid = _angle_invalid(record)
        fallback = any(item['fallback'] for item in candidates)
        if stage >= 2 and invalid:
            description += f" This record contains an invalid angle calculation; the recorded numerical safeguard retains C{record['safeguard_id']}."
        elif stage >= 2 and fallback:
            description += f" C{record['safeguard_id']} is retained outside the cone by the smallest-angle safeguard."
        angle = f"{candidate['angle_deg']:.3f}°" if candidate['angle_deg'] is not None else 'unavailable'
        threshold = f"{record['half_angle_deg']:.3f}°" if record['half_angle_deg'] is not None else 'unavailable'
        detail = f"C{inspected} · source {candidate['source_direction']} · offspring {candidate['offspring']}"
        if stage >= 2:
            detail += f" · angle {angle} / limit {threshold} · {_status(candidate, record)}"
        if stage >= 3:
            detail += f" · score {candidate['weighted_score']:.5f}"
        if not _visible(candidate, record, stage):
            detail += ' · kept in the inspector; this neighbor enters the displayed pool at Pool'
    else:
        diagram = _profile(record, noisy=True, height=240)
        objective = _profile(record, noisy=False, height=240)
        left_title, right_title = 'Noisy stream · standardized coordinates', 'Saved clean design · original units'
        description = ('The initial Gaussian stream and its saved clean design are different states. No candidates exist yet.'
                       if frame['phase'] == 'initial' else 'The recorded noisy stream is moving, while its saved clean design stays fixed. Proposal generation and selection begin at step 128.')
        detail = 'No candidate pool at this time. The before/after lines show actual recorded values, without interpolated motion.'
    if not candidates:
        count_label, count_value = 'Candidate pool', 'No candidates yet'
    elif stage == 0:
        count_label, count_value = 'Own offspring', f'{own_count} generated'
    elif stage == 1:
        count_label, count_value = 'Candidate pool', f'{len(candidates)} pooled'
    else:
        count_label, count_value = 'After filtering', f'{admitted} / {len(candidates)} retained'
    show_archive = not candidates or stage == 4
    return {
        'diagram': diagram, 'objective': objective,
        'profile': _profile(record, candidate, show_after=show_archive),
        'left_title': left_title, 'right_title': right_title,
        'left_subtitle': 'Membership diagram' if candidates else 'Recorded before / after states',
        'right_subtitle': 'Both objectives minimized' if candidates else 'All 30 variables in [0,1]',
        'heading': STAGES[stage] if candidates else ('Initialize' if frame['phase'] == 'initial' else 'Flow transport'),
        'description': description, 'detail': detail, 'candidate_id': inspected,
        'time': f"Step {step} / 160 · t = {frame['time']:.3f}",
        'counts': {'own': own_count, 'pool': len(candidates), 'admitted': admitted,
                   'visible': sum(_visible(item, record, stage) for item in candidates)},
        'count_label': count_label, 'count_value': count_value,
        'winner': (f"C{chosen['id']}" if stage >= 3 else 'Awaiting selection') if chosen else '—',
        'score': (f"{record['archive_score_before']:.4f} → {record['archive_score_after']:.4f}"
                  if show_archive else f"{record['archive_score_before']:.4f}"),
        'score_label': 'Archive score ↑' if show_archive else 'Archive score before ↑',
        'archive': ('Updated' if record['updated'] else 'Retained') if show_archive else 'Awaiting archive',
        'sources': list(_source_colors(record).items()),
        'has_candidates': bool(candidates),
        'record_href': full_record_href(mode, step, direction, STAGES[stage] if candidates else None, inspected),
    }


def full_record_href(mode, step, direction, stage=None, candidate_id=None):
    """Link the rendered method scene to exactly the same detailed record."""
    context = {'mode': mode, 'step': int(step), 'direction': int(direction)}
    if stage is not None:
        context['stage'] = stage
    if candidate_id is not None:
        context['candidate'] = int(candidate_id)
    return '/process/?' + urlencode(context)


TOUR_CONTROL = """
function(play, reset, tick, mode, step, direction, disabled, phase, availability) {
  const trigger = window.dash_clientside.callback_context.triggered || [];
  const changed = new Set(trigger.map(item => item.prop_id));
  const steps = (availability[mode] || {})[String(direction)] || [];
  const available = steps.includes(Number(step));
  const options = ['Generate', 'Pool', 'Filter', 'Select', 'Archive']
    .map((label, value) => ({label, value, disabled: !available}));
  const first = steps.length ? steps[0] : null;
  const status = first === null
    ? 'This direction has no recorded candidate decisions.'
    : `Step ${step} has no candidate pool. Stage playback starts at step ${first}.`;
  function result(stopped, label, value) {
    return [stopped, label, value, !available, options,
      available ? {display:'none'} : {},
      first === null ? 'No recorded decision' : `Go to first decision · step ${first}`,
      first === null, available ? '' : status];
  }
  // Inspect current record inputs synchronously. A late timer or pending server
  // render must never animate stages that do not exist in the selected record.
  if (!available) return result(true, 'Play stages', null);
  let current = Math.max(0, Math.min(4, Number(phase) || 0));
  if (changed.has('method-reset.n_clicks')) return result(true, 'Play stages', 0);
  if (changed.has('method-mode.value') || changed.has('method-time.value') || changed.has('method-direction.value'))
    return result(true, 'Play stages', 0);
  if (changed.has('method-play.n_clicks')) {
    if (disabled) return result(false, 'Pause stages', current === 4 ? 0 : current);
    return result(true, 'Play stages', current);
  }
  if (disabled) return result(true, 'Play stages', current);
  const next = Math.min(4, current + 1);
  return result(next === 4, next === 4 ? 'Play stages' : 'Pause stages', next);
}
"""


FIRST_DECISION = """
function(clicks, mode, direction, availability) {
  const steps = (availability[mode] || {})[String(direction)] || [];
  return clicks && steps.length ? steps[0] : window.dash_clientside.no_update;
}
"""


def create_method_panel(server):
    trace = load_trace()
    app = Dash('method_atelier', server=server, url_base_pathname='/method/',
               assets_folder=str(Path(__file__).resolve().parent / 'assets'),
               title='ParetoFlow · One real sampling decision')
    server.add_url_rule('/method', endpoint='method_atelier_redirect', view_func=lambda: redirect('/method/'))
    app.layout = html.Div([
        dcc.Store(id='method-availability', data=decision_steps(trace)),
        dcc.Store(id='method-inspected'), dcc.Interval(id='method-clock', interval=1900, disabled=True),
        html.Div([
            html.Div([html.Span('PARETOFLOW / RECORDED METHOD', className='atelier-eyebrow'),
                      html.H2('Watch a sampling decision take shape'),
                      html.P('Follow real offspring from neighboring streams into one selected state.', className='atelier-subtitle')]),
            html.A('Full record ↗', id='method-full-record', href=full_record_href('guided', 140, 300, 'Generate'),
                   target='_blank', className='atelier-link'),
        ], className='atelier-head'),
        html.Div([
            html.Div([html.Label('Configuration'), dcc.Dropdown(id='method-mode', options=[{'label': value['label'], 'value': key} for key, value in trace['modes'].items()], value='guided', clearable=False)], className='atelier-field method-configuration'),
            html.Div([html.Label('Receiving direction'), dcc.Dropdown(id='method-direction', options=[{'label': f'Direction {value}', 'value': value} for value in trace['directions']], value=300, clearable=False)], className='atelier-field'),
            html.Div([html.Button('Play stages', id='method-play', n_clicks=0, className='atelier-primary'),
                      html.Button('Reset', id='method-reset', n_clicks=0)], className='method-play-controls'),
        ], className='atelier-controls method-controls'),
        html.Div([html.Span(id='method-time-label'), dcc.Slider(id='method-time', min=0, max=160, step=1, value=140,
                  marks={0:'0',80:'80',128:'128 · selection begins',160:'160'}, updatemode='mouseup')], className='method-timeline'),
        dcc.RadioItems(id='method-phase', options=[{'label': name, 'value': index} for index, name in enumerate(STAGES)],
                       value=0, inline=True, className='atelier-stages'),
        html.Div([
            html.Span(id='method-stage-status', role='status'),
            html.Button('Go to first decision', id='method-first-decision', n_clicks=0),
        ], id='method-decision-shortcut', className='method-decision-shortcut', style={'display':'none'}),
        html.Div([html.Strong(id='method-heading'), html.Span(id='method-description')], className='atelier-readout method-description'),
        html.Div([
            html.Section([html.Div([html.H3(id='method-left-title'), html.Span(id='method-left-subtitle', className='atelier-kicker')], className='atelier-card-head'),
                          dcc.Graph(id='method-diagram', config=CONFIG)], className='atelier-card'),
            html.Section([html.Div([html.H3(id='method-right-title'), html.Span(id='method-right-subtitle', className='atelier-kicker')], className='atelier-card-head'),
                          dcc.Graph(id='method-objective', config=CONFIG)], className='atelier-card'),
        ], className='atelier-grid'),
        html.Div([html.Div(id='method-source-legend', className='atelier-legend'),
                  html.Div([html.Span('× Excluded'), html.Span('★ Selected'), html.Span('○ Inspecting')],
                           id='method-candidate-legend', className='atelier-legend')], className='method-legends'),
        html.Div([
            html.Div([html.Span('Own offspring', id='method-count-label'), html.Strong(id='method-count')], className='atelier-stat'),
            html.Div([html.Span('Selected state'), html.Strong(id='method-winner')], className='atelier-stat'),
            html.Div([html.Span('Archive score before ↑', id='method-score-label'), html.Strong(id='method-score')], className='atelier-stat'),
            html.Div([html.Span('Saved design'), html.Strong(id='method-archive')], className='atelier-stat'),
        ], className='atelier-stats'),
        html.Div([
            html.Div([html.Strong('Inspect a candidate', id='method-inspector-title'), html.P(id='method-detail'),
                      html.Span('Click a candidate in either plot. Its clean endpoint appears in amber; the saved archive is teal.',
                                id='method-inspector-hint', className='atelier-caption')], className='method-inspector-copy'),
            html.Div([dcc.Graph(id='method-profile', config=CONFIG), html.Span('30 clean-design variables · original [0,1] units', className='atelier-caption')], className='method-profile'),
        ], className='method-inspector'),
        html.P('Stages reveal decisions within one recorded step; positions in the membership diagram are schematic. '
               'The objective plot uses original-unit proxy predictions; filtering uses standardized score vectors. '
               'Candidate IDs reset when the record changes. Training was completed before these records.', className='atelier-note'),
    ], className='atelier atelier-panel method-atelier')

    app.clientside_callback(TOUR_CONTROL,
        Output('method-clock', 'disabled'), Output('method-play', 'children'), Output('method-phase', 'value'),
        Output('method-play', 'disabled'), Output('method-phase', 'options'),
        Output('method-decision-shortcut', 'style'), Output('method-first-decision', 'children'),
        Output('method-first-decision', 'disabled'), Output('method-stage-status', 'children'),
        Input('method-play', 'n_clicks'), Input('method-reset', 'n_clicks'), Input('method-clock', 'n_intervals'),
        Input('method-mode', 'value'), Input('method-time', 'value'), Input('method-direction', 'value'),
        State('method-clock', 'disabled'), State('method-phase', 'value'), State('method-availability', 'data'))

    app.clientside_callback(FIRST_DECISION, Output('method-time', 'value'),
        Input('method-first-decision', 'n_clicks'), State('method-mode', 'value'),
        State('method-direction', 'value'), State('method-availability', 'data'), prevent_initial_call=True)

    @app.callback(Output('method-inspected', 'data'), Input('method-diagram', 'clickData'),
                  Input('method-objective', 'clickData'), Input('method-mode', 'value'),
                  Input('method-time', 'value'), Input('method-direction', 'value'), prevent_initial_call=True)
    def inspect(diagram, objective, mode, step, direction):
        if ctx.triggered_id in ('method-mode', 'method-time', 'method-direction'):
            return None
        click = diagram if ctx.triggered_id == 'method-diagram' else objective
        if not click or not click.get('points'):
            return no_update
        identifier = click['points'][0].get('customdata')
        if not isinstance(identifier, (int, float)):
            return no_update
        return {'record': [mode, int(step), int(direction)], 'id': int(identifier)}

    @app.callback(
        Output('method-diagram', 'figure'), Output('method-objective', 'figure'), Output('method-profile', 'figure'),
        Output('method-left-title', 'children'), Output('method-right-title', 'children'),
        Output('method-left-subtitle', 'children'), Output('method-right-subtitle', 'children'),
        Output('method-heading', 'children'), Output('method-description', 'children'), Output('method-time-label', 'children'),
        Output('method-count', 'children'), Output('method-winner', 'children'), Output('method-score', 'children'),
        Output('method-archive', 'children'), Output('method-detail', 'children'), Output('method-source-legend', 'children'),
        Output('method-candidate-legend', 'style'), Output('method-candidate-legend', 'children'),
        Output('method-inspector-title', 'children'),
        Output('method-inspector-hint', 'children'), Output('method-count-label', 'children'),
        Output('method-score-label', 'children'), Output('method-full-record', 'href'),
        Input('method-mode', 'value'), Input('method-time', 'value'), Input('method-direction', 'value'),
        Input('method-phase', 'value'), Input('method-inspected', 'data'))
    def render(mode, step, direction, stage, selection):
        identifier = selection.get('id') if selection and selection.get('record') == [mode, int(step), int(direction)] else None
        scene = method_scene(trace, mode, int(step), int(direction), stage, identifier)
        legend_items = [html.Span('○ Inspecting')]
        if stage is not None and stage >= 2:
            legend_items.insert(0, html.Span('× Excluded'))
        if stage is not None and stage >= 3:
            legend_items.insert(1, html.Span('★ Selected'))
        if scene['has_candidates']:
            legends = [html.Span([html.I(style={'backgroundColor': color}), f'Direction {source}']) for source, color in scene['sources']]
            title = 'Inspect a candidate'
            hint = ('Candidate in amber; archive before in gray and after in teal.' if stage == 4 else
                    'Click a candidate to inspect its clean endpoint in amber. Gray shows the archive before this decision.')
        else:
            legends = [html.Span([html.I(style={'backgroundColor': color}), label])
                       for label, color in [('Before', GRAY), ('After', TEAL)]]
            title = 'Saved clean design'
            hint = 'Move the time slider to compare recorded stream states, or jump to the first candidate decision above.'
        return (scene['diagram'], scene['objective'], scene['profile'], scene['left_title'], scene['right_title'], scene['left_subtitle'], scene['right_subtitle'],
                scene['heading'], scene['description'], scene['time'],
                scene['count_value'], scene['winner'],
                scene['score'], scene['archive'], scene['detail'], legends,
                {} if scene['has_candidates'] else {'display':'none'}, legend_items, title, hint,
                scene['count_label'], scene['score_label'], scene['record_href'])
    return app
