/**
 * AuraCast - Professional Weather & Machine Learning Client Controller
 * Features Progressive Loading: Instant OpenWeather presentation followed by asynchronous ML prediction.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Live UTC Clock (runs on all pages)
    function updateClock() {
        const utcElem = document.getElementById('utc-clock');
        if (utcElem) {
            const now = new Date();
            utcElem.textContent = now.toUTCString().slice(17, 25) + ' UTC';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    // DOM Elements - Search & Location
    const searchForm = document.getElementById('search-form');
    if (!searchForm) return; // Only execute weather dashboard logic if search form exists on page

    const cityInput = document.getElementById('city-input');
    const clearSearchBtn = document.getElementById('clear-search-btn');
    const searchSuggestions = document.getElementById('search-suggestions');
    const searchSubmitBtn = document.getElementById('search-submit-btn');
    const geoLocationBtn = document.getElementById('geo-location-btn');
    const quickCityChips = document.querySelectorAll('.quick-city-chip');

    // DOM Elements - Error & Fallback Banners
    const errorBanner = document.getElementById('error-banner');
    const errorTitle = document.getElementById('error-title');
    const errorMessage = document.getElementById('error-message');
    const retryErrorBtn = document.getElementById('retry-error-btn');
    const fallbackBanner = document.getElementById('fallback-banner');
    const fallbackMessage = document.getElementById('fallback-message');

    // DOM Elements - Weather Hero (Skeleton & Content)
    const weatherHeroSkeleton = document.getElementById('weather-hero-skeleton');
    const weatherHeroContent = document.getElementById('weather-hero-content');
    const weatherSource = document.getElementById('weather-source');
    const heroCityName = document.getElementById('hero-city-name');
    const heroLocationCoords = document.getElementById('hero-location-coords');
    const heroWeatherIcon = document.getElementById('hero-weather-icon');
    const heroTemp = document.getElementById('hero-temp');
    const heroCondition = document.getElementById('hero-condition');
    const heroFeelsLike = document.getElementById('hero-feels-like');
    const heroTempMax = document.getElementById('hero-temp-max');
    const heroTempMin = document.getElementById('hero-temp-min');
    const heroObservedTime = document.getElementById('hero-observed-time');

    // DOM Elements - Metric Cards
    const metricSkeletons = document.querySelectorAll('.metric-skeleton');
    const metricValues = document.querySelectorAll('.metric-value');
    const metricHumidity = document.getElementById('metric-humidity');
    const metricPressure = document.getElementById('metric-pressure');
    const metricWindSpeed = document.getElementById('metric-wind-speed');
    const metricWindDir = document.getElementById('metric-wind-dir');
    const metricCloudiness = document.getElementById('metric-cloudiness');
    const metricVisibility = document.getElementById('metric-visibility');
    const metricSunrise = document.getElementById('metric-sunrise');
    const metricSunset = document.getElementById('metric-sunset');

    // DOM Elements - 24h Baseline Forecast
    const hourlyForecastSkeleton = document.getElementById('hourly-forecast-skeleton');
    const hourlyForecastContainer = document.getElementById('hourly-forecast-container');

    // DOM Elements - Prediction / ML Card (Skeleton, Content, Error)
    const predictionCardSkeleton = document.getElementById('prediction-card-skeleton');
    const predictionCardContent = document.getElementById('prediction-card-content');
    const predictionCardError = document.getElementById('prediction-card-error');
    const retryPredictionBtn = document.getElementById('retry-prediction-btn');
    const mlRainProb = document.getElementById('ml-rain-prob');
    const mlRiskBadge = document.getElementById('ml-risk-badge');
    const mlRainDesc = document.getElementById('ml-rain-desc');
    const rainGaugeCircle = document.getElementById('rain-gauge-circle');

    // DOM Elements - 6-Hour ML Strip
    const mlStripSkeleton = document.getElementById('ml-strip-skeleton');
    const mlHourlyStrip = document.getElementById('ml-hourly-strip');

    // DOM Elements - Historical Trends
    const historicalTrendsSkeleton = document.getElementById('historical-trends-skeleton');
    const historicalTrendsContent = document.getElementById('historical-trends-content');
    const histMeanTemp = document.getElementById('hist-mean-temp');
    const histTempRange = document.getElementById('hist-temp-range');
    const histMeanHum = document.getElementById('hist-mean-hum');
    const histTotalPrecip = document.getElementById('hist-total-precip');
    const chartTabBtns = document.querySelectorAll('.chart-tab-btn');

    // DOM Elements - Model Validation Modal
    const mlMetricsModal = document.getElementById('ml-metrics-modal');
    const toggleMlModalBtn = document.getElementById('toggle-ml-modal-btn');
    const closeMlModalBtn = document.getElementById('close-ml-modal-btn');
    const evalTempMae = document.getElementById('eval-temp-mae');
    const evalTempRmse = document.getElementById('eval-temp-rmse');
    const evalHumMae = document.getElementById('eval-hum-mae');
    const evalHumRmse = document.getElementById('eval-hum-rmse');
    const evalRainAcc = document.getElementById('eval-rain-acc');
    const evalRainF1 = document.getElementById('eval-rain-f1');
    const evalRainPrec = document.getElementById('eval-rain-prec');
    const evalRainRec = document.getElementById('eval-rain-rec');
    const evalFeatureImportanceList = document.getElementById('eval-feature-importance-list');

    // Internal State
    let currentTrendData = [];
    let trendChartInstance = null;
    let activeMetric = 'temperature';
    let lastSearchParams = { city: 'Kolkata' };
    let currentResolvedCoords = null; // { lat, lon }
    let debounceTimer = null;

    // Live UTC Clock
    function updateClock() {
        const utcElem = document.getElementById('utc-clock');
        if (utcElem) {
            const now = new Date();
            utcElem.textContent = now.toUTCString().slice(17, 25) + ' UTC';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    // =========================================================================
    // PROGRESSIVE LOADING CONTROLLER
    // =========================================================================

    /**
     * Primary entrypoint: Fetches current weather instantly, then triggers async ML prediction.
     */
    async function loadWeatherData(params) {
        lastSearchParams = params;
        hideError();
        setWeatherLoading(true);
        setPredictionLoading(true);

        try {
            const query = new URLSearchParams(params).toString();
            const response = await fetch(`/api/weather/current?${query}`);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Unable to retrieve weather (${response.status})`);
            }

            const data = await response.json();
            
            // Step 1: Render fast OpenWeather data immediately
            renderCurrentWeather(data);
            setWeatherLoading(false);

            // Step 2: Extract coordinates and asynchronously fetch ML prediction
            if (data.location && data.location.latitude != null && data.location.longitude != null) {
                currentResolvedCoords = {
                    lat: data.location.latitude,
                    lon: data.location.longitude
                };
                fetchPredictionData(currentResolvedCoords.lat, currentResolvedCoords.lon);
            }
        } catch (err) {
            console.error('Weather fetch error:', err);
            setWeatherLoading(false);
            setPredictionLoading(false);
            showError('Location Lookup Notice', err.message || 'Could not retrieve weather data. Please try searching again.');
        }
    }

    /**
     * Asynchronously fetches ML prediction and 30-day historical analysis.
     */
    async function fetchPredictionData(lat, lon) {
        setPredictionLoading(true);
        setPredictionError(false);

        try {
            const response = await fetch(`/api/prediction?lat=${lat}&lon=${lon}`);

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `ML prediction failed (${response.status})`);
            }

            const predData = await response.json();
            renderPredictionBundle(predData);
            setPredictionLoading(false);
        } catch (err) {
            console.warn('ML Prediction fetch error:', err);
            setPredictionLoading(false);
            setPredictionError(true);
        }
    }

    // =========================================================================
    // RENDERING FUNCTIONS
    // =========================================================================

    /**
     * Render OpenWeather observation & 24h baseline forecast.
     */
    function renderCurrentWeather(data) {
        if (!data || !data.current) return;

        const loc = data.location;
        const curr = data.current;
        const metrics = curr.metrics;

        // 1. Fallback Notice
        if (data.is_fallback && data.message) {
            fallbackBanner.classList.remove('hidden');
            fallbackMessage.textContent = data.message;
        } else {
            fallbackBanner.classList.add('hidden');
        }

        // 2. Hero Weather Section
        heroCityName.textContent = loc.city + (loc.country ? `, ${loc.country}` : '');
        heroLocationCoords.textContent = `${loc.state ? loc.state + ' • ' : ''}${Math.abs(loc.latitude).toFixed(2)}°${loc.latitude >= 0 ? 'N' : 'S'}, ${Math.abs(loc.longitude).toFixed(2)}°${loc.longitude >= 0 ? 'E' : 'W'}`;
        weatherSource.textContent = curr.source ? curr.source.toUpperCase() : 'LIVE OBSERVATION';
        heroTemp.textContent = `${Math.round(metrics.temperature)}°`;
        heroCondition.textContent = curr.description;
        heroFeelsLike.textContent = `${metrics.feels_like}°C`;
        heroTempMax.textContent = `${Math.round(metrics.temp_max)}°`;
        heroTempMin.textContent = `${Math.round(metrics.temp_min)}°`;
        heroObservedTime.textContent = curr.observed_at;
        heroWeatherIcon.src = `/static/icons/${curr.icon || 'cloudy'}.svg`;

        // 3. Metrics Grid
        metricHumidity.textContent = `${metrics.humidity}%`;
        metricPressure.textContent = `${metrics.pressure}`;
        metricWindSpeed.textContent = `${metrics.wind_speed}`;
        metricWindDir.textContent = `${metrics.wind_direction_compass || 'N'} (${metrics.wind_direction_deg || 0}°)`;
        metricCloudiness.textContent = `${metrics.cloudiness}%`;
        metricVisibility.textContent = `${metrics.visibility != null ? metrics.visibility : 10.0}`;
        metricSunrise.textContent = curr.sunrise || '--:--';
        metricSunset.textContent = curr.sunset || '--:--';

        // 4. 24-Hour Baseline Forecast Cards
        hourlyForecastContainer.innerHTML = '';
        if (data.hourly_forecast && data.hourly_forecast.length > 0) {
            data.hourly_forecast.forEach(item => {
                const card = document.createElement('div');
                card.className = 'flex-shrink-0 w-20 bg-[#172032] border border-white/[0.06] rounded-xl p-2.5 flex flex-col items-center justify-between text-center';
                card.innerHTML = `
                    <span class="text-[11px] text-slate-400 font-medium">${item.time}</span>
                    <img src="/static/icons/${item.icon || 'cloudy'}.svg" alt="${item.condition}" class="w-6 h-6 my-1.5 object-contain">
                    <span class="text-xs font-bold text-white">${Math.round(item.temperature)}°</span>
                    <span class="text-[10px] text-slate-400 mt-0.5">${item.humidity}%</span>
                `;
                hourlyForecastContainer.appendChild(card);
            });
        }
    }

    /**
     * Render ML prediction, 6h hourly predictions, and 30-day historical chart.
     */
    function renderPredictionBundle(bundle) {
        if (!bundle || !bundle.prediction) return;

        const pred = bundle.prediction;
        const hist = bundle.historical || {};

        // 1. ML Rain Probability & Gauge
        const rainProb = pred.rain_probability_next_24h != null ? pred.rain_probability_next_24h : 0;
        mlRainProb.textContent = `${Math.round(rainProb)}%`;

        // Gauge circumference is 2 * pi * 40 ≈ 251.2
        const offset = 251.2 - (251.2 * (rainProb / 100));
        rainGaugeCircle.style.strokeDashoffset = offset;

        // Risk badge formatting
        const riskLevel = pred.rain_risk_level || 'Low';
        mlRiskBadge.textContent = `${riskLevel} Risk`;

        if (riskLevel === 'Low') {
            mlRiskBadge.className = 'inline-block px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 text-xs font-semibold';
            rainGaugeCircle.setAttribute('class', 'text-emerald-400 stroke-current transition-all duration-700 ease-out');
            mlRainDesc.textContent = 'Precipitation is unlikely over the next 24 hours.';
        } else if (riskLevel === 'Moderate') {
            mlRiskBadge.className = 'inline-block px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 border border-amber-500/20 text-xs font-semibold';
            rainGaugeCircle.setAttribute('class', 'text-amber-400 stroke-current transition-all duration-700 ease-out');
            mlRainDesc.textContent = 'Possible isolated showers or scattered rain.';
        } else {
            mlRiskBadge.className = 'inline-block px-2 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20 text-xs font-semibold';
            rainGaugeCircle.setAttribute('class', 'text-rose-400 stroke-current transition-all duration-700 ease-out');
            mlRainDesc.textContent = 'High probability of continuous rain or thunderstorms.';
        }

        // 2. ML 6-Hour Prediction Strip
        mlHourlyStrip.innerHTML = '';
        if (pred.hourly_predictions && pred.hourly_predictions.length > 0) {
            pred.hourly_predictions.forEach(item => {
                const card = document.createElement('div');
                card.className = 'bg-[#172032] border border-white/[0.06] rounded-xl p-3 flex flex-col justify-between text-center';
                card.innerHTML = `
                    <div class="text-[11px] text-slate-400 font-medium">${item.time}</div>
                    <div class="my-1.5">
                        <span class="text-lg font-bold text-white">${Math.round(item.temperature)}°</span>
                        <span class="text-xs text-slate-400">C</span>
                    </div>
                    <div class="space-y-0.5 text-[10px]">
                        <div class="text-sky-300 font-medium">${item.humidity}% RH</div>
                        <div class="text-slate-400">${Math.round(item.rain_probability)}% rain</div>
                    </div>
                `;
                mlHourlyStrip.appendChild(card);
            });
        }

        // 3. Historical Trends Summary & Interactive Chart
        histMeanTemp.textContent = `${hist.avg_temperature != null ? hist.avg_temperature : '--'}°C`;
        histTempRange.textContent = `${hist.min_temperature != null ? hist.min_temperature : '--'}° / ${hist.max_temperature != null ? hist.max_temperature : '--'}°`;
        histMeanHum.textContent = `${hist.avg_humidity != null ? hist.avg_humidity : '--'}%`;
        histTotalPrecip.textContent = `${hist.total_precipitation != null ? hist.total_precipitation : '--'} mm`;

        currentTrendData = hist.recent_trend || [];
        renderTrendChart(activeMetric);

        // 4. Populate Model Validation Modal
        const evalM = pred.evaluation;
        if (evalM) {
            evalTempMae.textContent = `${evalM.temperature_mae} °C`;
            evalTempRmse.textContent = `${evalM.temperature_rmse} °C`;
            evalHumMae.textContent = `${evalM.humidity_mae} %`;
            evalHumRmse.textContent = `${evalM.humidity_rmse} %`;
            evalRainAcc.textContent = `${(evalM.rain_accuracy * 100).toFixed(1)}%`;
            evalRainF1.textContent = `${evalM.rain_f1.toFixed(2)}`;
            evalRainPrec.textContent = `${(evalM.rain_precision * 100).toFixed(1)}%`;
            evalRainRec.textContent = `${(evalM.rain_recall * 100).toFixed(1)}%`;

            // Feature Importance list
            evalFeatureImportanceList.innerHTML = '';
            if (pred.feature_importance) {
                for (const [feat, weight] of Object.entries(pred.feature_importance)) {
                    const featRow = document.createElement('div');
                    featRow.className = 'flex items-center justify-between text-xs bg-[#172032] p-2 rounded-lg border border-white/[0.05]';
                    featRow.innerHTML = `
                        <span class="font-mono text-slate-300 text-[11px]">${feat}</span>
                        <div class="flex items-center gap-2">
                            <div class="w-20 bg-slate-800 rounded-full h-1.5 overflow-hidden">
                                <div class="bg-sky-400 h-full rounded-full" style="width: ${Math.min(weight * 200, 100)}%"></div>
                            </div>
                            <span class="font-medium text-sky-300 w-7 text-right text-[11px]">${weight}</span>
                        </div>
                    `;
                    evalFeatureImportanceList.appendChild(featRow);
                }
            }
        }
    }

    // =========================================================================
    // CHART RENDERING
    // =========================================================================

    function renderTrendChart(metricKey) {
        const ctx = document.getElementById('historical-trend-chart');
        if (!ctx || !currentTrendData || currentTrendData.length === 0) return;

        if (trendChartInstance) {
            trendChartInstance.destroy();
        }

        const labels = currentTrendData.map(d => d.time);
        let values = [];
        let labelName = 'Temperature (°C)';
        let strokeColor = '#38bdf8'; // sky-400
        let fillColor = 'rgba(56, 189, 248, 0.08)';

        if (metricKey === 'temperature') {
            values = currentTrendData.map(d => d.temperature);
            labelName = 'Temperature (°C)';
            strokeColor = '#38bdf8';
            fillColor = 'rgba(56, 189, 248, 0.08)';
        } else if (metricKey === 'humidity') {
            values = currentTrendData.map(d => d.humidity);
            labelName = 'Humidity (%)';
            strokeColor = '#22d3ee';
            fillColor = 'rgba(34, 211, 238, 0.08)';
        } else if (metricKey === 'precipitation') {
            values = currentTrendData.map(d => d.precipitation);
            labelName = 'Precipitation (mm)';
            strokeColor = '#818cf8';
            fillColor = 'rgba(129, 140, 248, 0.2)';
        } else if (metricKey === 'wind_speed') {
            values = currentTrendData.map(d => d.wind_speed);
            labelName = 'Wind Speed (m/s)';
            strokeColor = '#f59e0b';
            fillColor = 'rgba(245, 158, 11, 0.08)';
        }

        trendChartInstance = new Chart(ctx, {
            type: metricKey === 'precipitation' ? 'bar' : 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: labelName,
                    data: values,
                    borderColor: strokeColor,
                    backgroundColor: fillColor,
                    borderWidth: 2,
                    tension: 0.35,
                    pointRadius: 0,
                    pointHoverRadius: 4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#172032',
                        titleColor: '#e2e8f0',
                        bodyColor: '#38bdf8',
                        borderColor: 'rgba(255, 255, 255, 0.1)',
                        borderWidth: 1,
                        padding: 8,
                        titleFont: { size: 11 },
                        bodyFont: { size: 11 },
                        displayColors: false
                    }
                },
                scales: {
                    x: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: {
                            color: '#64748b',
                            maxTicksLimit: 7,
                            font: { size: 10 }
                        }
                    },
                    y: {
                        grid: { color: 'rgba(255, 255, 255, 0.04)' },
                        ticks: {
                            color: '#64748b',
                            font: { size: 10 }
                        }
                    }
                }
            }
        });
    }

    // Chart tab switch handlers
    chartTabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            chartTabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeMetric = btn.getAttribute('data-metric');
            renderTrendChart(activeMetric);
        });
    });

    // =========================================================================
    // SKELETON / LOADING / ERROR STATE HELPERS
    // =========================================================================

    function setWeatherLoading(isLoading) {
        if (isLoading) {
            weatherHeroSkeleton.classList.remove('hidden');
            weatherHeroContent.classList.add('hidden');
            
            metricSkeletons.forEach(el => el.classList.remove('hidden'));
            metricValues.forEach(el => el.classList.add('hidden'));

            hourlyForecastSkeleton.classList.remove('hidden');
            hourlyForecastContainer.classList.add('hidden');

            searchSubmitBtn.disabled = true;
            searchSubmitBtn.classList.add('opacity-75');
        } else {
            weatherHeroSkeleton.classList.add('hidden');
            weatherHeroContent.classList.remove('hidden');

            metricSkeletons.forEach(el => el.classList.add('hidden'));
            metricValues.forEach(el => el.classList.remove('hidden'));

            hourlyForecastSkeleton.classList.add('hidden');
            hourlyForecastContainer.classList.remove('hidden');

            searchSubmitBtn.disabled = false;
            searchSubmitBtn.classList.remove('opacity-75');
        }
    }

    function setPredictionLoading(isLoading) {
        if (isLoading) {
            predictionCardSkeleton.classList.remove('hidden');
            predictionCardContent.classList.add('hidden');
            predictionCardError.classList.add('hidden');

            mlStripSkeleton.classList.remove('hidden');
            mlHourlyStrip.classList.add('hidden');

            historicalTrendsSkeleton.classList.remove('hidden');
            historicalTrendsContent.classList.add('hidden');
        } else {
            predictionCardSkeleton.classList.add('hidden');
            mlStripSkeleton.classList.add('hidden');
            historicalTrendsSkeleton.classList.add('hidden');
        }
    }

    function setPredictionError(hasError) {
        if (hasError) {
            predictionCardSkeleton.classList.add('hidden');
            predictionCardContent.classList.add('hidden');
            predictionCardError.classList.remove('hidden');

            mlStripSkeleton.classList.add('hidden');
            mlHourlyStrip.classList.add('hidden');

            historicalTrendsSkeleton.classList.add('hidden');
            historicalTrendsContent.classList.add('hidden');
        } else {
            predictionCardError.classList.add('hidden');
            predictionCardContent.classList.remove('hidden');
            mlHourlyStrip.classList.remove('hidden');
            historicalTrendsContent.classList.remove('hidden');
        }
    }

    function showError(title, msg) {
        errorTitle.textContent = title;
        errorMessage.textContent = msg;
        errorBanner.classList.remove('hidden');
    }

    function hideError() {
        errorBanner.classList.add('hidden');
    }

    // =========================================================================
    // EVENT LISTENERS & INTERACTION HANDLERS
    // =========================================================================

    // Search Form Submit Handler
    searchForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const city = cityInput.value.trim();
        if (city) {
            searchSuggestions.classList.add('hidden');
            loadWeatherData({ city: city });
        }
    });

    // Quick Popular Location Chips Click
    quickCityChips.forEach(chip => {
        chip.addEventListener('click', () => {
            const city = chip.getAttribute('data-city');
            cityInput.value = city;
            clearSearchBtn.classList.remove('hidden');
            loadWeatherData({ city: city });
        });
    });

    // Geolocation Handler
    geoLocationBtn.addEventListener('click', () => {
        if (!navigator.geolocation) {
            showError('Geolocation Unavailable', 'Your browser does not support location detection.');
            return;
        }

        geoLocationBtn.classList.add('opacity-75');
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                geoLocationBtn.classList.remove('opacity-75');
                cityInput.value = '';
                loadWeatherData({
                    lat: pos.coords.latitude,
                    lon: pos.coords.longitude
                });
            },
            (err) => {
                geoLocationBtn.classList.remove('opacity-75');
                showError('Location Permission Notice', err.message || 'Please enable location permissions in your browser or search for your city.');
            },
            { timeout: 10000, enableHighAccuracy: false }
        );
    });

    // Search Autocomplete Suggestion Logic
    cityInput.addEventListener('input', () => {
        const val = cityInput.value.trim();
        if (val.length > 0) {
            clearSearchBtn.classList.remove('hidden');
        } else {
            clearSearchBtn.classList.add('hidden');
            searchSuggestions.classList.add('hidden');
            return;
        }

        if (val.length < 2) {
            searchSuggestions.classList.add('hidden');
            return;
        }

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            try {
                const res = await fetch(`/api/location/search?q=${encodeURIComponent(val)}`);
                if (res.ok) {
                    const results = await res.json();
                    if (results && results.length > 0) {
                        searchSuggestions.innerHTML = '';
                        results.forEach(loc => {
                            const item = document.createElement('div');
                            item.className = 'px-3.5 py-2 text-xs text-slate-200 hover:bg-[#1e2a40] hover:text-sky-300 cursor-pointer flex justify-between items-center transition-colors';
                            item.innerHTML = `
                                <span class="font-medium">${loc.name}${loc.state ? ', ' + loc.state : ''}</span>
                                <span class="text-slate-400 font-mono text-[10px]">${loc.country}</span>
                            `;
                            item.addEventListener('click', () => {
                                cityInput.value = `${loc.name}, ${loc.country}`;
                                searchSuggestions.classList.add('hidden');
                                loadWeatherData({ lat: loc.latitude, lon: loc.longitude });
                            });
                            searchSuggestions.appendChild(item);
                        });
                        searchSuggestions.classList.remove('hidden');
                    } else {
                        searchSuggestions.classList.add('hidden');
                    }
                }
            } catch (e) {
                // Ignore autocomplete errors silently
            }
        }, 300);
    });

    clearSearchBtn.addEventListener('click', () => {
        cityInput.value = '';
        clearSearchBtn.classList.add('hidden');
        searchSuggestions.classList.add('hidden');
        cityInput.focus();
    });

    // Close autocomplete on click outside
    document.addEventListener('click', (e) => {
        if (!searchForm.contains(e.target)) {
            searchSuggestions.classList.add('hidden');
        }
    });

    // Global Retry Button Handler
    if (retryErrorBtn) {
        retryErrorBtn.addEventListener('click', () => {
            hideError();
            loadWeatherData(lastSearchParams);
        });
    }

    // Prediction Retry Button Handler
    if (retryPredictionBtn) {
        retryPredictionBtn.addEventListener('click', () => {
            if (currentResolvedCoords) {
                fetchPredictionData(currentResolvedCoords.lat, currentResolvedCoords.lon);
            } else {
                loadWeatherData(lastSearchParams);
            }
        });
    }

    // ML Modal Open/Close Handlers
    if (toggleMlModalBtn) {
        toggleMlModalBtn.addEventListener('click', () => {
            mlMetricsModal.classList.remove('hidden');
        });
    }

    if (closeMlModalBtn) {
        closeMlModalBtn.addEventListener('click', () => {
            mlMetricsModal.classList.add('hidden');
        });
    }

    if (mlMetricsModal) {
        mlMetricsModal.addEventListener('click', (e) => {
            if (e.target === mlMetricsModal) {
                mlMetricsModal.classList.add('hidden');
            }
        });
    }

    // Initial Weather Load (Default: Kolkata)
    loadWeatherData({ city: 'Kolkata' });
});
