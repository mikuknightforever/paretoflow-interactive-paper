/**
 * Local replacement for MyST 1.3.1 HoverPopover.
 * This factory is injected unchanged into both the browser and SSR bundles.
 * Keep it self-contained: the patcher serializes the function with toString().
 */
function createHoverPopover(React, HoverCard) {
  return function HoverPopover({ children, openDelay = 400, card, side, arrowClass = 'fill-white' }) {
    const [load, setLoad] = React.useState(false);
    const [open, setOpen] = React.useState(false);
    const closeTimer = React.useRef(null);
    const trigger = React.useRef(null);
    const content = React.useRef(null);

    function cancelClose() {
      if (closeTimer.current !== null) {
        clearTimeout(closeTimer.current);
        closeTimer.current = null;
      }
    }

    function isWithinPopover(target) {
      return !!target && typeof target.nodeType === 'number' &&
        (trigger.current?.contains(target) || content.current?.contains(target));
    }

    function enter(event) {
      if (event.pointerType === 'touch') return;
      cancelClose();
      setLoad(true);
    }

    function leave(event) {
      if (event.pointerType === 'touch' || isWithinPopover(event.relatedTarget)) return;
      cancelClose();
      // Radix 1.0.x can retain a stale, document-wide text-selection flag and
      // refuse its own close request. Own this timer locally so moving away
      // always closes this card, without modifying the user's selection.
      closeTimer.current = setTimeout(() => {
        closeTimer.current = null;
        setOpen(false);
      }, 300);
    }

    React.useEffect(() => cancelClose, []);

    function changeOpen(next) {
      if (!next) cancelClose();
      setOpen(next);
    }

    return React.createElement(HoverCard.Root, { open, onOpenChange: changeOpen, openDelay },
      React.createElement(HoverCard.Trigger, {
        asChild: true, ref: trigger, onPointerEnter: enter, onPointerLeave: leave,
        onMouseEnter: enter, onFocus: enter, onBlur: leave,
      }, children),
      React.createElement(HoverCard.Portal, null,
        React.createElement(HoverCard.Content, {
          ref: content, className: 'exclude-from-outline hover-card-content',
          sideOffset: 5, side, onPointerEnter: enter, onPointerLeave: leave,
          onFocus: enter, onBlur: leave,
        }, typeof card === 'function' ? load && card({ load }) : card,
        React.createElement(HoverCard.Arrow, { className: arrowClass })),
      ),
    );
  };
}

module.exports = createHoverPopover;
