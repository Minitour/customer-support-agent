// Cross-component "fly to cart" animation.
//
// The Navbar registers its cart icon as the landing target; product cards call
// flyToCart() with their own element. We clone the source, position the clone
// over it, then animate a damped spring (transform + opacity only, so it stays
// on the compositor) toward the cart icon.

let target: HTMLElement | null = null;

export function registerFlyTarget(el: HTMLElement | null) {
  target = el;
}

function prefersReducedMotion() {
  return (
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

interface SpringOptions {
  stiffness?: number;
  damping?: number;
  mass?: number;
}

// Samples a damped-spring response curve (0 → 1, with overshoot) and returns
// the normalized progress at each fixed time step plus the total settle time.
function springProgress({ stiffness = 230, damping = 22, mass = 1 }: SpringOptions) {
  const omega0 = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));

  const dt = 1 / 120; // sample at ~120fps
  const maxTime = 2; // seconds, hard cap
  const restThreshold = 0.001;

  const samples: number[] = [];
  let settleTime = maxTime;

  for (let t = 0; t <= maxTime; t += dt) {
    let x: number;
    if (zeta < 1) {
      const omegaD = omega0 * Math.sqrt(1 - zeta * zeta);
      const envelope = Math.exp(-zeta * omega0 * t);
      x =
        1 -
        envelope *
          (Math.cos(omegaD * t) + ((zeta * omega0) / omegaD) * Math.sin(omegaD * t));
    } else {
      // critically / over-damped: no oscillation
      const envelope = Math.exp(-omega0 * t);
      x = 1 - envelope * (1 + omega0 * t);
    }
    samples.push(x);
    if (Math.abs(1 - x) < restThreshold) {
      settleTime = t;
      break;
    }
  }

  return { samples, settleTime };
}

export function flyToCart(source: HTMLElement) {
  if (!target || prefersReducedMotion()) return;

  const src = source.getBoundingClientRect();
  const dst = target.getBoundingClientRect();
  if (src.width === 0 || src.height === 0) return;

  const dx = dst.left + dst.width / 2 - (src.left + src.width / 2);
  const dy = dst.top + dst.height / 2 - (src.top + src.height / 2);

  const clone = source.cloneNode(true) as HTMLElement;
  clone.style.position = "fixed";
  clone.style.left = `${src.left}px`;
  clone.style.top = `${src.top}px`;
  clone.style.width = `${src.width}px`;
  clone.style.height = `${src.height}px`;
  clone.style.margin = "0";
  clone.style.zIndex = "9999";
  clone.style.pointerEvents = "none";
  clone.style.transformOrigin = "center center";
  clone.style.willChange = "transform, opacity";
  clone.style.boxShadow = "0 12px 28px rgba(0,0,0,0.18)";
  document.body.appendChild(clone);

  const { samples, settleTime } = springProgress({ stiffness: 230, damping: 24 });
  const duration = Math.min(900, Math.max(480, settleTime * 1000));

  const minScale = 0.12;
  const fadeStart = 0.78;

  const keyframes: Keyframe[] = samples.map((p, i) => {
    const offset = samples.length > 1 ? i / (samples.length - 1) : 1;
    const scale = 1 - (1 - minScale) * p;
    const opacity = p < fadeStart ? 1 : Math.max(0, 1 - (p - fadeStart) / (1 - fadeStart));
    return {
      offset,
      transform: `translate(${dx * p}px, ${dy * p}px) scale(${scale})`,
      opacity,
    };
  });

  const animation = clone.animate(keyframes, {
    duration,
    easing: "linear",
    fill: "forwards",
  });

  animation.finished
    .catch(() => {})
    .finally(() => {
      clone.remove();
      bumpTarget();
    });
}

// Small "received" reaction on the cart icon when an item lands.
function bumpTarget() {
  if (!target || prefersReducedMotion()) return;
  target.animate(
    [
      { transform: "scale(1)" },
      { transform: "scale(1.22)" },
      { transform: "scale(1)" },
    ],
    { duration: 320, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
  );
}
