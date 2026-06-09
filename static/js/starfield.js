/**
 * AetherStarfield — lightweight, unique, miniature space canvas.
 * No external deps. Reusable. Subtle and premium.
 */
(function () {
  window.AetherStarfield = function (canvas, opts = {}) {
    const ctx = canvas.getContext('2d', { alpha: true });
    let w = 0, h = 0;
    let stars = [];
    const options = {
      count: opts.count || 180,
      speed: opts.speed || 0.08,
      color: opts.color || '#00e5ff',
      twinkle: true,
    };

    function resize() {
      const rect = canvas.getBoundingClientRect();
      w = canvas.width = Math.floor(rect.width * devicePixelRatio);
      h = canvas.height = Math.floor(rect.height * devicePixelRatio);
      canvas.style.width = rect.width + 'px';
      canvas.style.height = rect.height + 'px';
      initStars();
    }

    function initStars() {
      stars = [];
      for (let i = 0; i < options.count; i++) {
        stars.push({
          x: Math.random() * w,
          y: Math.random() * h,
          z: Math.random() * 0.8 + 0.4,
          r: Math.random() * 1.4 + 0.6,
          tw: Math.random() * Math.PI * 2,
        });
      }
    }

    function draw() {
      ctx.clearRect(0, 0, w, h);
      ctx.fillStyle = options.color;
      ctx.strokeStyle = options.color;

      for (let s of stars) {
        const alpha = 0.6 + Math.sin(s.tw) * 0.35;
        ctx.globalAlpha = alpha * s.z;
        ctx.beginPath();
        ctx.arc(s.x, s.y, s.r * s.z, 0, Math.PI * 2);
        ctx.fill();

        // subtle movement (drift)
        s.y += options.speed * s.z;
        s.tw += 0.03;
        if (s.y > h) {
          s.y = 0;
          s.x = Math.random() * w;
        }
      }
      ctx.globalAlpha = 1;

      // occasional shooting star (very rare, premium feel)
      if (Math.random() < 0.008) {
        const sx = Math.random() * w * 0.6;
        const sy = Math.random() * h * 0.4;
        ctx.strokeStyle = 'rgba(255,255,255,0.9)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + 120 + Math.random() * 60, sy + 40 + Math.random() * 30);
        ctx.stroke();
        ctx.lineWidth = 1;
      }

      requestAnimationFrame(draw);
    }

    function bind() {
      window.addEventListener('resize', () => {
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.style.width = rect.width + 'px';
        canvas.style.height = rect.height + 'px';
        resize();
      });
      // Click to fire a comet
      canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const cx = (e.clientX - rect.left) * devicePixelRatio;
        const cy = (e.clientY - rect.top) * devicePixelRatio;
        for (let i = 0; i < 6; i++) {
          stars.push({
            x: cx + (Math.random() - 0.5) * 30,
            y: cy + (Math.random() - 0.5) * 20,
            z: 1.1,
            r: 1.8,
            tw: 0,
          });
        }
      });
    }

    resize();
    bind();
    draw();
  };
})();
