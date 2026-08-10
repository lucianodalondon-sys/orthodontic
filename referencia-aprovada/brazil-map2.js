/* BrazilMap2 — real geometry (Natural Earth via world-atlas TopoJSON) projected with d3-geo.
   Technical model lit in the dark: translucent shape, cyan stroke, point cloud,
   radial light pool, and the seasonality curve drawn loose in empty space. */
(function () {
  var R = window.React;
  var TOPO = "https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json";

  function waitLibs() {
    return new Promise(function (res) {
      (function tick() {
        if (window.d3 && window.topojson) return res();
        setTimeout(tick, 40);
      })();
    });
  }

  var _brazil = null;
  function loadBrazil() {
    if (_brazil) return _brazil;
    _brazil = waitLibs()
      .then(function () { return fetch(TOPO); })
      .then(function (r) { return r.json(); })
      .then(function (topo) {
        var fc = window.topojson.feature(topo, topo.objects.countries);
        return fc.features.filter(function (x) {
          return String(x.id) === "076" || (x.properties && x.properties.name === "Brazil");
        })[0];
      });
    return _brazil;
  }

  function mulberry32(a) {
    return function () {
      a |= 0; a = (a + 0x6D2B79F5) | 0;
      var t = Math.imul(a ^ (a >>> 15), 1 | a);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  /* Metro anchors (real coordinates) weighted like a national dental-franchise footprint. */
  var ANCHORS = [
    [-46.63, -23.55, 46], [-43.20, -22.91, 22], [-43.94, -19.92, 20], [-49.27, -25.43, 13],
    [-51.23, -30.03, 13], [-48.55, -27.59, 8], [-47.88, -15.79, 10], [-49.25, -16.68, 9],
    [-47.06, -22.90, 12], [-47.81, -21.18, 8], [-38.51, -12.97, 12], [-34.88, -8.05, 10],
    [-38.54, -3.72, 10], [-35.21, -5.79, 5], [-34.86, -7.12, 4], [-35.73, -9.65, 4],
    [-37.07, -10.91, 3], [-44.30, -2.53, 4], [-42.80, -5.09, 4], [-48.50, -1.46, 5],
    [-60.02, -3.10, 5], [-56.10, -15.60, 5], [-54.62, -20.44, 5], [-40.34, -20.32, 5],
    [-48.28, -18.92, 4], [-48.85, -26.30, 3], [-51.18, -29.17, 3], [-46.33, -23.96, 4],
    [-49.38, -20.81, 3], [-63.90, -8.76, 2], [-67.81, -9.97, 1], [-48.33, -10.18, 2],
    [-51.07, 0.03, 1], [-60.67, 2.82, 1], [-40.50, -9.39, 2], [-40.84, -14.86, 2],
    [-43.86, -16.73, 2], [-43.35, -21.76, 3], [-47.46, -23.50, 4], [-49.06, -22.32, 3],
    [-52.62, -27.10, 2], [-52.34, -31.77, 2], [-53.81, -29.68, 2], [-47.49, -5.53, 2],
    [-49.13, -5.37, 1], [-55.51, -11.86, 1], [-44.99, -12.15, 1], [-39.27, -7.23, 2],
    [-45.89, -23.18, 3], [-51.55, -25.09, 2]
  ];

  function buildPoints(brazil, n) {
    var rnd = mulberry32(20260807);
    var total = ANCHORS.reduce(function (s, a) { return s + a[2]; }, 0);
    var pts = [];
    for (var i = 0; i < ANCHORS.length && pts.length < n; i++) {
      var a = ANCHORS[i];
      var count = Math.max(1, Math.round((a[2] / total) * n));
      for (var k = 0; k < count && pts.length < n; k++) {
        var ok = false, lon, lat, tries = 0;
        while (!ok && tries < 40) {
          var rad = 0.25 + rnd() * 1.5;
          var ang = rnd() * Math.PI * 2;
          lon = a[0] + Math.cos(ang) * rad;
          lat = a[1] + Math.sin(ang) * rad * 0.85;
          ok = window.d3.geoContains(brazil, [lon, lat]);
          tries++;
        }
        if (ok) pts.push([lon, lat]);
      }
    }
    while (pts.length < n) {
      var lo = -70 + rnd() * 35, la = -32 + rnd() * 30;
      if (window.d3.geoContains(brazil, [lo, la])) pts.push([lo, la]);
    }
    return pts.slice(0, n);
  }

  /* The five measured points of the seasonality series. No invented months. */
  var SERIES = [["JUL", 34], ["AGO", 23], ["SET", 22], ["DEZ", 7.9], ["JAN", 2.5]];

  function BrazilMap2(props) {
    var ref = R.useRef(null);
    var live = props.live || [];
    var reduced = !!props.reduced;
    var liveRef = R.useRef(live); liveRef.current = live;
    var hoverRef = R.useRef(props.onHover); hoverRef.current = props.onHover;
    var selRef = R.useRef(props.onSelect); selRef.current = props.onSelect;

    R.useEffect(function () {
      var el = ref.current, killed = false, ro = null;
      loadBrazil().then(function (brazil) {
        if (killed || !el || !brazil) return;
        var d3 = window.d3;
        var dim = buildPoints(brazil, 336);

        function draw() {
          if (!el) return;
          var w = el.clientWidth, h = el.clientHeight;
          if (!w || !h) return;
          d3.select(el).selectAll("svg").remove();
          var svg = d3.select(el).append("svg")
            .attr("width", w).attr("height", h)
            .attr("viewBox", "0 0 " + w + " " + h)
            .style("display", "block").style("overflow", "visible");

          var defs = svg.append("defs");
          var glow = defs.append("filter").attr("id", "od2Glow")
            .attr("x", "-120%").attr("y", "-120%").attr("width", "340%").attr("height", "340%");
          glow.append("feGaussianBlur").attr("stdDeviation", 6).attr("result", "b");
          var mg = glow.append("feMerge");
          mg.append("feMergeNode").attr("in", "b");
          mg.append("feMergeNode").attr("in", "SourceGraphic");

          var pool = defs.append("radialGradient").attr("id", "od2Pool");
          pool.append("stop").attr("offset", "0%").attr("stop-color", "rgba(0,185,255,.20)");
          pool.append("stop").attr("offset", "60%").attr("stop-color", "rgba(0,185,255,.07)");
          pool.append("stop").attr("offset", "100%").attr("stop-color", "rgba(0,185,255,0)");

          var proj = d3.geoMercator().fitExtent([[30, 26], [w - 30, h - 30]], brazil);
          var path = d3.geoPath(proj);
          var b = path.bounds(brazil);

          /* light pool under the object */
          svg.append("ellipse")
            .attr("cx", (b[0][0] + b[1][0]) / 2).attr("cy", b[1][1] - 6)
            .attr("rx", (b[1][0] - b[0][0]) * 0.62).attr("ry", 46)
            .attr("fill", "url(#od2Pool)").attr("opacity", 1);

          svg.append("path").datum(brazil).attr("d", path)
            .attr("fill", "rgba(0,185,255,.045)")
            .attr("stroke", "rgba(0,185,255,.42)").attr("stroke-width", 1)
            .attr("opacity", 1)
            .style("animation", reduced ? null : "odIn 700ms cubic-bezier(.2,.7,.3,1)");

          /* the 336 unheard praças */
          var dots = svg.append("g").attr("opacity", 1)
            .style("animation", reduced ? null : "odDotsIn 1100ms cubic-bezier(.2,.7,.3,1)");
          dim.forEach(function (p) {
            var xy = proj(p);
            if (xy) dots.append("circle").attr("cx", xy[0]).attr("cy", xy[1]).attr("r", 2.1)
              .attr("fill", "rgba(255,255,255,.14)");
          });

          /* seasonality curve, loose in empty space, left of the shape */
          var cx0 = 14, cw = Math.max(84, b[0][0] - 30), ch = 108;
          var cy0 = b[1][1] - ch - 26;
          if (cw >= 84 && cy0 > 30) {
            var x = d3.scalePoint().domain(SERIES.map(function (s) { return s[0]; })).range([cx0, cx0 + cw]);
            var y = d3.scaleLinear().domain([0, 36]).range([cy0 + ch, cy0]);
            var line = d3.line().curve(d3.curveCatmullRom.alpha(.6))
              .x(function (s) { return x(s[0]); }).y(function (s) { return y(s[1]); });
            var cg = svg.append("g").attr("opacity", 1)
              .style("animation", reduced ? null : "odCurveIn 1500ms cubic-bezier(.2,.7,.3,1)");
            cg.append("path").datum(SERIES).attr("d", line)
              .attr("fill", "none").attr("stroke", "rgba(0,185,255,.42)").attr("stroke-width", 1);
            SERIES.forEach(function (s) {
              cg.append("circle").attr("cx", x(s[0])).attr("cy", y(s[1])).attr("r", s[1] === 34 ? 3 : 1.8)
                .attr("fill", s[1] === 34 ? "#00B9FF" : "rgba(255,255,255,.34)");
              cg.append("text").text(s[0])
                .attr("x", x(s[0])).attr("y", cy0 + ch + 14).attr("text-anchor", "middle")
                .attr("fill", "rgba(255,255,255,.34)").attr("font-size", 8.5)
                .attr("letter-spacing", ".12em")
                .style("font-family", '"IBM Plex Mono",monospace');
            });
            cg.append("text").text("JUL · ÍNDICE 34")
              .attr("x", x("JUL")).attr("y", y(34) - 12).attr("text-anchor", "middle")
              .attr("fill", "rgba(255,255,255,.72)").attr("font-size", 9.5)
              .attr("letter-spacing", ".14em")
              .style("font-family", '"IBM Plex Mono",monospace');
          }

          /* the 4 praças with intelligence */
          var lg = svg.append("g");
          liveRef.current.forEach(function (c, i) {
            var xy = proj([c.lon, c.lat]);
            if (!xy) return;
            var g = lg.append("g").attr("transform", "translate(" + xy[0] + "," + xy[1] + ")")
              .style("cursor", "pointer").attr("opacity", 1)
              .style("animation", reduced ? null : "odLitIn " + (1300 + i * 260) + "ms cubic-bezier(.2,.7,.3,1)");
            g.append("circle").attr("r", 22).attr("fill", "rgba(0,185,255,.10)")
              .attr("stroke", "rgba(0,185,255,.35)").attr("stroke-width", 1)
              .attr("class", reduced ? "" : "od-map-halo").style("animation-delay", (i * 260) + "ms");
            g.append("circle").attr("r", 9).attr("fill", "rgba(0,185,255,.22)");
            g.append("circle").attr("r", 4.6).attr("fill", "#00B9FF").attr("filter", "url(#od2Glow)");
            var flip = xy[0] > w - 150;
            g.append("text").text(c.short)
              .attr("x", flip ? -30 : 30).attr("y", c.ly || 4)
              .attr("text-anchor", flip ? "end" : "start")
              .attr("fill", "rgba(255,255,255,.86)")
              .attr("font-size", 12).attr("font-weight", 700).attr("letter-spacing", ".04em")
              .style("font-family", '"Gotham","Montserrat",sans-serif')
              .style("pointer-events", "none");
            g.append("circle").attr("r", 26).attr("fill", "transparent")
              .on("mouseenter", function () {
                if (hoverRef.current) hoverRef.current(c.id, xy[0], xy[1]);
              })
              .on("mouseleave", function () { if (hoverRef.current) hoverRef.current(null); })
              .on("click", function () { if (selRef.current) selRef.current(c.id); });
          });
        }

        draw();
        if (window.ResizeObserver) {
          ro = new ResizeObserver(function () { draw(); });
          ro.observe(el);
        }
      });
      return function () { killed = true; if (ro) ro.disconnect(); };
    }, [reduced]);

    return R.createElement("div", {
      ref: ref,
      style: { position: "absolute", inset: 0, width: "100%", height: "100%" }
    });
  }

  window.BrazilMap2 = BrazilMap2;
})();
