/**
 * Aether Cosmos — Advanced Three.js miniature extraterrestrial Constellation Navigator
 * Heavy-duty premium 3D interactive for the Aether language academy.
 * Per approved plan: particles + Language Sector nodes (glowing, colored) + elegant trajectory lines.
 * Mouse/touch orbit, hover tooltips (DOM synced glass), click -> filter/nav or highlight.
 * Slow autonomous rotation + GSAP-interop hooks + breathing pulses.
 * Graceful fallback (caller decides). Performance minded. RTL/ Persian friendly (labels via data).
 * No external deps beyond Three (loaded in base). Designed to feel like a spacecraft HUD.
 */
(function () {
  window.AetherCosmos = function (mountEl, options = {}) {
    if (!mountEl) return null;
    if (typeof THREE === 'undefined') {
      console.warn('[AetherCosmos] Three.js not loaded — using graceful 2D fallback if provided.');
      return null;
    }

    const opts = Object.assign({
      width: mountEl.clientWidth || 800,
      height: mountEl.clientHeight || 420,
      nodeCount: 7,
      particleCount: 420,
      autoRotateSpeed: 0.00018,
      accentCyan: '#00e5ff',
      accentViolet: '#7c3aed',
      accentRose: '#ff4d94',
      languages: [], // [{name, slug, accent_color, short_desc}]
      onNodeClick: null, // (lang) => {}
      onNodeHover: null,
    }, options);

    let width = opts.width;
    let height = opts.height;
    let renderer, scene, camera, nodes = [], lines = [], particles;
    let raycaster, mouse, tooltipEl;
    let raf = null;
    let isDragging = false;
    let prevX = 0, prevY = 0;
    let rotY = 0.6, rotX = 0.15;

    // Create canvas container
    const canvas = document.createElement('canvas');
    canvas.style.width = '100%';
    canvas.style.height = '100%';
    canvas.style.display = 'block';
    canvas.style.borderRadius = 'inherit';
    mountEl.appendChild(canvas);

    function initThree() {
      renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: 'high-performance' });
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.6));
      renderer.setSize(width, height);

      scene = new THREE.Scene();

      camera = new THREE.PerspectiveCamera(52, width / height, 0.1, 200);
      camera.position.set(0, 0.6, 5.8);

      raycaster = new THREE.Raycaster();
      mouse = new THREE.Vector2();

      // Soft ambient + key lights for holographic glass feel
      const amb = new THREE.AmbientLight(0x404060, 0.55);
      scene.add(amb);
      const key = new THREE.DirectionalLight(0x00e5ff, 0.7);
      key.position.set(4, 6, 3);
      scene.add(key);
      const rim = new THREE.DirectionalLight(0x7c3aed, 0.35);
      rim.position.set(-6, -2, -4);
      scene.add(rim);

      // Background subtle nebula plane (uses CSS layered + low opacity 3D plane if desired; keep light)
      const nebulaGeo = new THREE.PlaneGeometry(18, 11);
      const nebulaMat = new THREE.MeshBasicMaterial({
        color: 0x0a0f1f,
        transparent: true,
        opacity: 0.08,
        depthWrite: false
      });
      const nebula = new THREE.Mesh(nebulaGeo, nebulaMat);
      nebula.position.z = -4.5;
      scene.add(nebula);

      createStarfieldParticles();
      createLanguageNodes();
      createTrajectoryLines();

      // Tooltip glass element (synced to DOM for premium text + RTL)
      tooltipEl = document.createElement('div');
      tooltipEl.className = 'cosmos-tooltip glass hidden';
      tooltipEl.style.position = 'absolute';
      tooltipEl.style.pointerEvents = 'none';
      tooltipEl.style.zIndex = '70';
      tooltipEl.style.padding = '8px 14px';
      tooltipEl.style.fontSize = '12px';
      tooltipEl.style.borderRadius = '12px';
      tooltipEl.style.whiteSpace = 'nowrap';
      tooltipEl.style.backdropFilter = 'blur(16px)';
      mountEl.style.position = mountEl.style.position || 'relative';
      mountEl.appendChild(tooltipEl);

      bindEvents();
      animate();
      handleResize();

      // Initial gentle ignition animation hook (callable by GSAP if wanted)
      setTimeout(() => igniteNodes(0.35), 420);
    }

    function createStarfieldParticles() {
      const geo = new THREE.BufferGeometry();
      const positions = [];
      const colors = [];
      const sizes = [];
      const c1 = new THREE.Color(opts.accentCyan);
      const c2 = new THREE.Color(opts.accentViolet);

      for (let i = 0; i < opts.particleCount; i++) {
        const r = 7.5 + Math.random() * 3.2;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        const x = r * Math.sin(phi) * Math.cos(theta);
        const y = r * Math.sin(phi) * Math.sin(theta) * 0.6;
        const z = r * Math.cos(phi) - 1.2;

        positions.push(x, y, z);

        const col = Math.random() > 0.6 ? c1 : c2;
        colors.push(col.r, col.g, col.b);
        sizes.push(0.7 + Math.random() * 1.8);
      }

      geo.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      geo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      geo.setAttribute('size', new THREE.Float32BufferAttribute(sizes, 1));

      const mat = new THREE.PointsMaterial({
        size: 0.032,
        vertexColors: true,
        transparent: true,
        opacity: 0.75,
        depthWrite: false,
        blending: THREE.AdditiveBlending
      });

      particles = new THREE.Points(geo, mat);
      scene.add(particles);
    }

    function createLanguageNodes() {
      nodes = [];
      const langs = (opts.languages && opts.languages.length) ? opts.languages : defaultLangs();

      const radius = 2.65;
      const step = (Math.PI * 2) / Math.max(langs.length, 1);

      langs.forEach((lang, idx) => {
        const angle = idx * step - 0.7;
        const x = Math.cos(angle) * radius;
        const z = Math.sin(angle) * radius * 0.82 - 0.1;
        const y = Math.sin(idx * 1.7) * 0.55;

        const colorHex = lang.accent_color || opts.accentCyan;
        const col = new THREE.Color(colorHex);

        // Core glowing node — icosa or sphere for miniature planet feel
        const geo = new THREE.IcosahedronGeometry(0.22, 1);
        const mat = new THREE.MeshPhongMaterial({
          color: col,
          emissive: col,
          emissiveIntensity: 0.35,
          shininess: 22,
          transparent: true,
          opacity: 0.95
        });
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.set(x, y, z);
        mesh.userData = { lang, baseScale: 1.0, idx };

        // Outer holographic ring (thin torus)
        const ringGeo = new THREE.TorusGeometry(0.38, 0.018, 10, 28);
        const ringMat = new THREE.MeshBasicMaterial({ color: col, transparent: true, opacity: 0.28 });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = 1.1 + idx * 0.1;
        mesh.add(ring);

        scene.add(mesh);
        nodes.push(mesh);

        // Subtle point light per node for "holographic" local illumination
        const light = new THREE.PointLight(col.getHex(), 0.6, 6);
        light.position.copy(mesh.position);
        scene.add(light);
        mesh.userData.light = light;
      });
    }

    function createTrajectoryLines() {
      lines = [];
      if (nodes.length < 2) return;

      // Elegant thin connections between "nearby" sectors (cluster Romance + others lightly)
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          if (Math.random() > 0.58) continue; // sparse, premium, not cluttered

          const a = nodes[i].position;
          const b = nodes[j].position;

          const pts = [];
          pts.push(a.clone());
          // gentle arc midpoint
          const mid = a.clone().add(b).multiplyScalar(0.5);
          mid.y += 0.18 + Math.random() * 0.12;
          pts.push(mid);
          pts.push(b.clone());

          const geo = new THREE.BufferGeometry().setFromPoints(pts);
          const mat = new THREE.LineBasicMaterial({
            color: 0x00e5ff,
            transparent: true,
            opacity: 0.12,
            linewidth: 1
          });
          const line = new THREE.Line(geo, mat);
          scene.add(line);
          lines.push(line);
        }
      }
    }

    function defaultLangs() {
      return [
        { name: 'انگلیسی', slug: 'english', accent_color: '#00e5ff', short_desc: 'فرماندهی جهانی' },
        { name: 'فرانسوی', slug: 'french', accent_color: '#7c3aed', short_desc: 'دقت و ظرافت' },
        { name: 'آلمانی', slug: 'german', accent_color: '#22c55e', short_desc: 'مهندسی و عمق' },
        { name: 'اسپانیایی', slug: 'spanish', accent_color: '#ff4d94', short_desc: 'ریتم و زندگی' },
        { name: 'ایتالیایی', slug: 'italian', accent_color: '#f59e0b', short_desc: 'ملودی و طراحی' },
      ];
    }

    function igniteNodes(targetOpacity = 0.95) {
      nodes.forEach((n, i) => {
        if (!n.material) return;
        const orig = n.material.opacity || 0.6;
        n.material.opacity = 0.25;
        // Simple manual pulse (GSAP can override if present)
        setTimeout(() => {
          if (n.material) n.material.opacity = targetOpacity;
        }, 90 + i * 55);
      });
    }

    function bindEvents() {
      const rect = () => canvas.getBoundingClientRect();

      window.addEventListener('resize', handleResize);

      // Orbit drag (mouse + touch)
      canvas.addEventListener('mousedown', (e) => { isDragging = true; prevX = e.clientX; prevY = e.clientY; });
      window.addEventListener('mouseup', () => { isDragging = false; });
      window.addEventListener('mousemove', (e) => {
        if (!isDragging) {
          updateHover(e.clientX, e.clientY, rect());
          return;
        }
        const dx = (e.clientX - prevX) * 0.0038;
        const dy = (e.clientY - prevY) * 0.0032;
        rotY += dx;
        rotX = Math.max(-0.9, Math.min(0.9, rotX + dy));
        prevX = e.clientX; prevY = e.clientY;
      });

      // Touch
      canvas.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) { isDragging = true; prevX = e.touches[0].clientX; prevY = e.touches[0].clientY; }
      }, { passive: true });
      window.addEventListener('touchend', () => { isDragging = false; });
      window.addEventListener('touchmove', (e) => {
        if (!isDragging || e.touches.length !== 1) return;
        const t = e.touches[0];
        const dx = (t.clientX - prevX) * 0.0036;
        const dy = (t.clientY - prevY) * 0.003;
        rotY += dx;
        rotX = Math.max(-0.85, Math.min(0.85, rotX + dy));
        prevX = t.clientX; prevY = t.clientY;
      }, { passive: true });

      // Click nodes
      canvas.addEventListener('click', (e) => {
        const hit = pickNode(e.clientX, e.clientY, rect());
        if (hit && opts.onNodeClick) {
          opts.onNodeClick(hit.userData.lang);
        } else if (hit) {
          // default: console or simple highlight pulse
          pulseNode(hit);
        }
      });

      // Accessibility hint
      canvas.setAttribute('aria-label', 'صورت فلکی تعاملی زبان‌ها — بکشید تا بچرخد، کلیک کنید برای انتخاب مسیر');
    }

    function pickNode(clientX, clientY, r) {
      mouse.x = ((clientX - r.left) / r.width) * 2 - 1;
      mouse.y = -((clientY - r.top) / r.height) * 2 + 1;
      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(nodes, true);
      return intersects.length ? intersects[0].object : null;
    }

    function updateHover(clientX, clientY, r) {
      const hit = pickNode(clientX, clientY, r);
      if (!tooltipEl) return;

      if (hit && hit.userData && hit.userData.lang) {
        const l = hit.userData.lang;
        tooltipEl.innerHTML = `<span style="color:${l.accent_color}">${l.name}</span><br><span style="opacity:.7;font-size:10px">${l.short_desc || ''}</span>`;
        tooltipEl.style.left = (clientX - r.left + 14) + 'px';
        tooltipEl.style.top = (clientY - r.top - 8) + 'px';
        tooltipEl.classList.remove('hidden');
        tooltipEl.style.display = 'block';
        canvas.style.cursor = 'pointer';
      } else {
        tooltipEl.style.display = 'none';
        canvas.style.cursor = 'grab';
      }
    }

    function pulseNode(node) {
      const orig = node.scale.x;
      node.scale.setScalar(orig * 1.35);
      if (node.userData.light) node.userData.light.intensity = 1.6;
      setTimeout(() => {
        if (node && node.scale) node.scale.setScalar(orig);
        if (node && node.userData && node.userData.light) node.userData.light.intensity = 0.6;
      }, 380);
    }

    function handleResize() {
      const r = mountEl.getBoundingClientRect();
      width = Math.max(320, r.width);
      height = Math.max(280, r.height || 420);
      if (renderer && camera) {
        renderer.setSize(width, height);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      }
    }

    function animate() {
      raf = requestAnimationFrame(animate);
      if (!scene || !renderer || !camera) return;

      // Slow autonomous constellation rotation (premium, not distracting)
      rotY += opts.autoRotateSpeed;
      scene.rotation.y = rotY;
      scene.rotation.x = rotX * 0.6;

      // Gentle breathing on nodes + local lights
      const t = Date.now() * 0.0012;
      nodes.forEach((n, i) => {
        const s = 0.96 + Math.sin(t * 1.6 + i) * 0.045;
        n.scale.setScalar(n.userData.baseScale * s);
        if (n.userData.light) {
          n.userData.light.intensity = 0.55 + Math.sin(t * 2.1 + i * 1.3) * 0.18;
        }
      });

      // Very subtle particle drift (alive cockpit)
      if (particles) {
        particles.rotation.y = t * 0.006;
      }

      renderer.render(scene, camera);
    }

    function dispose() {
      if (raf) cancelAnimationFrame(raf);
      if (renderer) renderer.dispose();
      if (tooltipEl && tooltipEl.parentNode) tooltipEl.parentNode.removeChild(tooltipEl);
      // Three objects GC'd on page nav in SPA-like but here full pages ok
    }

    // Public API (for GSAP or other controllers)
    const api = {
      ignite: igniteNodes,
      pulseNode: (idx) => { if (nodes[idx]) pulseNode(nodes[idx]); },
      rotateTo: (y, x) => { rotY = y || rotY; rotX = (x != null ? x : rotX); },
      dispose,
      getNodes: () => nodes,
    };

    initThree();
    return api;
  };

  // Convenience: auto-init if data attr present (optional progressive enhancement)
  document.addEventListener('DOMContentLoaded', () => {
    const auto = document.querySelector('[data-aether-cosmos]');
    if (auto && window.AetherCosmos && typeof THREE !== 'undefined') {
      const langs = [];
      try { langs.push(...JSON.parse(auto.dataset.langs || '[]')); } catch(e){}
      window.AetherCosmos(auto, { languages: langs, onNodeClick: (l) => {
        if (l && l.slug) window.location.href = '/courses/?lang=' + l.slug;
      }});
    }
  });
})();
