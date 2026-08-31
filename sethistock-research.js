(() => {
    const RESEARCH_API = "https://sethistock-api.onrender.com";
    let researchRequestId = 0;

    const pct = (value, digits = 1) => value === null || value === undefined || Number.isNaN(Number(value)) ? "--" : `${Number(value).toFixed(digits)}%`;
    const mult = (value) => value === null || value === undefined || Number.isNaN(Number(value)) ? "--" : `${Number(value).toFixed(1)}x`;

    function researchCard(label, id, suffix = "") {
        return `<div class="bg-gray-50 border border-gray-100 rounded-xl p-4">
            <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">${label}</p>
            <p id="${id}" class="text-2xl font-black text-gray-900">--${suffix}</p>
        </div>`;
    }

    function ensureResearchUI() {
        if (document.getElementById("research-labs")) return;

        const valuationLink = document.querySelector('nav a[href="#valuation"]');
        if (valuationLink && !document.querySelector('nav a[href="#research-labs"]')) {
            valuationLink.insertAdjacentHTML("beforebegin", '<a href="#research-labs" class="hover:text-blue-600 transition">Research</a>');
        }

        const valuation = document.getElementById("valuation");
        if (!valuation) return;

        const section = document.createElement("section");
        section.id = "research-labs";
        section.className = "mt-12 scroll-mt-24";
        section.innerHTML = `
            <div class="flex flex-col md:flex-row md:items-end justify-between gap-3 mb-6 border-b border-gray-200 pb-4">
                <div>
                    <div class="flex items-center gap-3">
                        <h3 class="text-2xl font-black text-gray-900">Research Labs</h3>
                        <span class="px-2.5 py-1 rounded-full bg-blue-50 border border-blue-100 text-[10px] font-black text-blue-700 uppercase tracking-widest">New</span>
                    </div>
                    <p class="text-sm text-gray-500 mt-1">How the stock behaves around earnings and how today's valuation compares with its own history.</p>
                </div>
                <p id="research-status" class="text-xs font-bold text-gray-400 uppercase tracking-widest">Search a stock to initialise</p>
            </div>

            <div class="grid grid-cols-1 xl:grid-cols-2 gap-8">
                <article class="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-200">
                    <div class="mb-6">
                        <p class="text-[10px] font-black text-purple-600 uppercase tracking-widest mb-1">Event Study</p>
                        <h4 class="text-xl font-black text-gray-900">Earnings Reaction Study</h4>
                        <p class="text-sm text-gray-500 mt-1">Historical share-price reactions around reported earnings.</p>
                    </div>

                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                        ${researchCard("Avg |1D Move|", "earnings-avg-abs")}
                        ${researchCard("Positive Reactions", "earnings-positive")}
                        ${researchCard("EPS Beat Rate", "earnings-beat")}
                        ${researchCard("Avg 5D Move", "earnings-5d")}
                    </div>

                    <div id="earnings-reaction-chart" class="w-full h-[300px]"></div>
                    <div id="earnings-reaction-empty" class="hidden py-16 text-center text-sm font-semibold text-gray-400"></div>

                    <div class="overflow-x-auto mt-3 max-h-[260px] overflow-y-auto">
                        <table class="w-full text-left text-xs">
                            <thead class="sticky top-0 bg-white text-gray-400 uppercase tracking-wider">
                                <tr>
                                    <th class="py-2 pr-3">Earnings</th>
                                    <th class="py-2 px-3">EPS Surprise</th>
                                    <th class="py-2 px-3">1D</th>
                                    <th class="py-2 pl-3">5D</th>
                                </tr>
                            </thead>
                            <tbody id="earnings-reaction-table" class="divide-y divide-gray-100"></tbody>
                        </table>
                    </div>
                </article>

                <article class="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-200">
                    <div class="mb-6">
                        <p class="text-[10px] font-black text-blue-600 uppercase tracking-widest mb-1">Self-Relative Valuation</p>
                        <h4 class="text-xl font-black text-gray-900">Historical Valuation Bands</h4>
                        <p class="text-sm text-gray-500 mt-1">Current trailing P/E versus reconstructed post-earnings P/E history.</p>
                    </div>

                    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-5">
                        ${researchCard("Current P/E", "valuation-current")}
                        ${researchCard("Historical Median", "valuation-median")}
                        ${researchCard("Current Percentile", "valuation-percentile")}
                        <div class="bg-gray-50 border border-gray-100 rounded-xl p-4">
                            <p class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Position</p>
                            <p id="valuation-label" class="text-sm font-black text-gray-900 leading-tight mt-2">--</p>
                        </div>
                    </div>

                    <div id="valuation-band-chart" class="w-full h-[300px]"></div>
                    <div id="valuation-band-empty" class="hidden py-16 text-center text-sm font-semibold text-gray-400"></div>

                    <div class="mt-4 bg-blue-50/70 border border-blue-100 rounded-xl p-4">
                        <p class="text-[11px] leading-relaxed text-blue-900"><strong>Method:</strong> after each earnings release, SethiStock sums the latest four reported quarterly EPS figures and divides the post-release share price by that trailing EPS. This keeps the comparison historical rather than applying today's earnings backwards.</p>
                    </div>
                </article>
            </div>`;

        valuation.parentNode.insertBefore(section, valuation);
    }

    function setResearchStatus(text, tone = "neutral") {
        const el = document.getElementById("research-status");
        if (!el) return;
        el.textContent = text;
        el.className = `text-xs font-bold uppercase tracking-widest ${tone === "error" ? "text-red-500" : tone === "live" ? "text-blue-600" : "text-gray-400"}`;
    }

    function setResearchLoading(ticker) {
        setResearchStatus(`Analysing ${ticker || "stock"}...`, "live");
        ["earnings-avg-abs", "earnings-positive", "earnings-beat", "earnings-5d", "valuation-current", "valuation-median", "valuation-percentile", "valuation-label"].forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = '<span class="inline-block h-5 w-16 bg-gray-200 rounded animate-pulse"></span>';
        });
        document.getElementById("earnings-reaction-empty")?.classList.add("hidden");
        document.getElementById("valuation-band-empty")?.classList.add("hidden");
    }

    function renderEarnings(study) {
        const chart = document.getElementById("earnings-reaction-chart");
        const empty = document.getElementById("earnings-reaction-empty");
        const table = document.getElementById("earnings-reaction-table");

        if (!study || !study.available || !study.events?.length) {
            chart.innerHTML = "";
            table.innerHTML = "";
            empty.textContent = study?.reason || "Earnings reaction history is unavailable for this security.";
            empty.classList.remove("hidden");
            ["earnings-avg-abs", "earnings-positive", "earnings-beat", "earnings-5d"].forEach(id => document.getElementById(id).textContent = "N/A");
            return;
        }

        const s = study.summary || {};
        document.getElementById("earnings-avg-abs").textContent = pct(s.average_abs_1d_move_pct);
        document.getElementById("earnings-positive").textContent = pct(s.positive_reaction_rate_pct, 0);
        document.getElementById("earnings-beat").textContent = pct(s.eps_beat_rate_pct, 0);
        document.getElementById("earnings-5d").textContent = pct(s.average_5d_move_pct);

        const chronological = [...study.events].reverse();
        const y = chronological.map(e => e.move_1d_pct);
        const markerColors = y.map(v => Number(v) >= 0 ? "#16a34a" : "#dc2626");
        const hover = chronological.map(e => `EPS surprise: ${e.surprise_pct === null ? "N/A" : pct(e.surprise_pct)}<br>5D move: ${e.move_5d_pct === null ? "N/A" : pct(e.move_5d_pct)}`);

        Plotly.newPlot(chart, [{
            x: chronological.map(e => e.earnings_date),
            y,
            type: "bar",
            marker: { color: markerColors },
            customdata: hover,
            hovertemplate: "%{x}<br>1D reaction: %{y:.2f}%<br>%{customdata}<extra></extra>"
        }], {
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { t: 12, r: 12, b: 45, l: 45 },
            font: { color: "#6b7280", size: 11 },
            xaxis: { gridcolor: "#f3f4f6", tickformat: "%b %y", fixedrange: true },
            yaxis: { title: "1D move (%)", gridcolor: "#e5e7eb", zerolinecolor: "#9ca3af", fixedrange: true }
        }, { displayModeBar: false, responsive: true });

        table.innerHTML = study.events.slice(0, 8).map(e => {
            const one = Number(e.move_1d_pct);
            const five = e.move_5d_pct === null ? null : Number(e.move_5d_pct);
            const surprise = e.surprise_pct === null ? "N/A" : pct(e.surprise_pct);
            return `<tr>
                <td class="py-2.5 pr-3 font-bold text-gray-700">${e.earnings_date}</td>
                <td class="py-2.5 px-3 font-semibold ${e.surprise_pct !== null && e.surprise_pct >= 0 ? "text-green-600" : "text-red-600"}">${surprise}</td>
                <td class="py-2.5 px-3 font-black ${one >= 0 ? "text-green-600" : "text-red-600"}">${pct(one)}</td>
                <td class="py-2.5 pl-3 font-black ${five !== null && five >= 0 ? "text-green-600" : "text-red-600"}">${five === null ? "N/A" : pct(five)}</td>
            </tr>`;
        }).join("");
    }

    function renderValuation(study) {
        const chart = document.getElementById("valuation-band-chart");
        const empty = document.getElementById("valuation-band-empty");

        document.getElementById("valuation-current").textContent = study?.current_pe ? mult(study.current_pe) : "N/A";

        if (!study || !study.available || !study.observations?.length) {
            chart.innerHTML = "";
            empty.textContent = study?.reason || "Historical valuation data is unavailable for this security.";
            empty.classList.remove("hidden");
            document.getElementById("valuation-median").textContent = "N/A";
            document.getElementById("valuation-percentile").textContent = "N/A";
            document.getElementById("valuation-label").textContent = "Insufficient history";
            return;
        }

        const b = study.bands;
        document.getElementById("valuation-median").textContent = mult(b.median);
        document.getElementById("valuation-percentile").textContent = study.current_percentile === null ? "N/A" : pct(study.current_percentile, 0);
        document.getElementById("valuation-label").textContent = study.valuation_label || "Historical range";

        const obs = study.observations;
        const shapes = [{
            type: "rect", xref: "paper", x0: 0, x1: 1, y0: b.p25, y1: b.p75,
            fillcolor: "rgba(37,99,235,0.08)", line: { width: 0 }, layer: "below"
        }, {
            type: "line", xref: "paper", x0: 0, x1: 1, y0: b.median, y1: b.median,
            line: { color: "#2563eb", width: 2, dash: "dash" }
        }];

        if (study.current_pe) {
            shapes.push({
                type: "line", xref: "paper", x0: 0, x1: 1, y0: study.current_pe, y1: study.current_pe,
                line: { color: "#111827", width: 2, dash: "dot" }
            });
        }

        Plotly.newPlot(chart, [{
            x: obs.map(o => o.date),
            y: obs.map(o => o.pe),
            type: "scatter",
            mode: "lines+markers",
            line: { color: "#2563eb", width: 2 },
            marker: { size: 7, color: "#ffffff", line: { color: "#2563eb", width: 2 } },
            customdata: obs.map(o => [o.price, o.ttm_eps]),
            hovertemplate: "%{x}<br>P/E: %{y:.1f}x<br>Price: $%{customdata[0]:.2f}<br>TTM EPS: %{customdata[1]:.3f}<extra></extra>"
        }], {
            paper_bgcolor: "rgba(0,0,0,0)",
            plot_bgcolor: "rgba(0,0,0,0)",
            margin: { t: 12, r: 12, b: 45, l: 45 },
            font: { color: "#6b7280", size: 11 },
            shapes,
            xaxis: { gridcolor: "#f3f4f6", tickformat: "%b %y", fixedrange: true },
            yaxis: { title: "Trailing P/E (x)", gridcolor: "#e5e7eb", fixedrange: true }
        }, { displayModeBar: false, responsive: true });
    }

    async function loadStockResearch(ticker) {
        ensureResearchUI();
        if (!ticker) return;
        const requestId = ++researchRequestId;
        setResearchLoading(ticker);

        try {
            const res = await fetch(`${RESEARCH_API}/api/research/${encodeURIComponent(ticker)}`);
            if (!res.ok) throw new Error(`Research API returned ${res.status}`);
            const data = await res.json();
            if (requestId !== researchRequestId) return;

            renderEarnings(data.earnings_reaction);
            renderValuation(data.valuation_bands);
            setResearchStatus(`${data.ticker || ticker} research updated`, "live");
        } catch (err) {
            if (requestId !== researchRequestId) return;
            console.error("SethiStock research load failed:", err);
            setResearchStatus("Research temporarily unavailable", "error");
            renderEarnings({ available: false, reason: "Could not load earnings research." });
            renderValuation({ available: false, reason: "Could not load valuation history." });
        }
    }

    function waitForMainAnalysis(requestedValue) {
        setResearchLoading(requestedValue);
        let attempts = 0;
        const timer = setInterval(() => {
            attempts += 1;
            const dash = document.getElementById("dashboard");
            const button = document.getElementById("search-btn");
            const resolvedTicker = document.getElementById("display-ticker")?.textContent?.trim();
            if (dash?.classList.contains("opacity-100") && !button?.disabled && resolvedTicker) {
                clearInterval(timer);
                loadStockResearch(resolvedTicker);
            } else if (attempts >= 80) {
                clearInterval(timer);
                setResearchStatus("Waiting for a successful stock analysis", "neutral");
            }
        }, 250);
    }

    function bootResearchLabs() {
        ensureResearchUI();
        const form = document.getElementById("search-form");
        const input = document.getElementById("ticker-input");
        if (form) {
            form.addEventListener("submit", () => {
                waitForMainAnalysis(input?.value?.trim() || "stock");
            });
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bootResearchLabs);
    } else {
        bootResearchLabs();
    }
})();
