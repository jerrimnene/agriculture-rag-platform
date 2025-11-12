/**
 * DATE & TIME INTELLIGENCE SYSTEM
 * 
 * Makes the platform aware of:
 * - Current date/time
 * - Agricultural seasons (Zimbabwe)
 * - Planting windows
 * - Harvest periods
 * - Market seasons
 * - Gives contextual recommendations
 */

const DateTimeIntelligence = {
    
    /**
     * Get current date/time info
     */
    getCurrentDateTime: function() {
        const now = new Date();
        return {
            date: now,
            year: now.getFullYear(),
            month: now.getMonth() + 1, // 1-12
            day: now.getDate(),
            dayOfWeek: now.getDay(), // 0-6 (Sunday-Saturday)
            hour: now.getHours(),
            timestamp: now.getTime()
        };
    },
    
    /**
     * Get Zimbabwe agricultural season
     */
    getCurrentSeason: function() {
        const dt = this.getCurrentDateTime();
        const month = dt.month;
        
        // Zimbabwe seasons (Southern Hemisphere)
        if (month >= 11 || month <= 3) {
            return {
                season: 'rainy',
                name: 'Rainy Season / Summer',
                period: 'November - March',
                activities: [
                    'Land preparation',
                    'Planting maize, tobacco, cotton',
                    'First weeding',
                    'Fertilizer application',
                    'Pest monitoring'
                ],
                shona: 'Zhizha / Chirimo',
                ndebele: 'Ihlobo / Isikhathi Sezimvula'
            };
        } else if (month >= 4 && month <= 6) {
            return {
                season: 'harvest',
                name: 'Harvest Season / Autumn',
                period: 'April - June',
                activities: [
                    'Harvesting summer crops',
                    'Post-harvest handling',
                    'Marketing produce',
                    'Land clearing',
                    'Soil testing'
                ],
                shona: 'Nguva Yekukohwa / Matsutso',
                ndebele: 'Isikhathi Sokuvuna / Ukwindla'
            };
        } else if (month >= 7 && month <= 9) {
            return {
                season: 'dry',
                name: 'Dry Season / Winter',
                period: 'July - September',
                activities: [
                    'Winter wheat planting',
                    'Irrigation farming',
                    'Livestock feeding programs',
                    'Farm infrastructure repairs',
                    'Planning for summer season'
                ],
                shona: 'Chando / Nguva Yekutonhora',
                ndebele: 'Ubusika / Isikhathi Esomile'
            };
        } else {
            return {
                season: 'preparation',
                name: 'Pre-Season / Spring',
                period: 'October',
                activities: [
                    'Final land preparation',
                    'Input procurement',
                    'Seed treatment',
                    'First rains monitoring',
                    'Budget finalization'
                ],
                shona: 'Chivabvu',
                ndebele: 'Intlakohlanga'
            };
        }
    },
    
    /**
     * Get planting window status for a crop
     */
    getPlantingWindow: function(cropName) {
        const dt = this.getCurrentDateTime();
        const month = dt.month;
        
        // Simplified planting windows for major crops
        const plantingWindows = {
            'TOBACCO': { start: 9, end: 11, optimal: 10 },
            'MAIZE': { start: 11, end: 1, optimal: 12 },
            'COTTON': { start: 11, end: 1, optimal: 12 },
            'SOYA': { start: 11, end: 1, optimal: 12 },
            'GROUNDNUTS': { start: 11, end: 1, optimal: 12 },
            'WHEAT': { start: 4, end: 6, optimal: 5 },
            'TOMATOES': { start: 9, end: 3, optimal: 10 },
            'CABBAGES': { start: 1, end: 12, optimal: 3 } // Year-round with irrigation
        };
        
        // Find matching crop (case-insensitive, partial match)
        let cropKey = null;
        for (let key in plantingWindows) {
            if (cropName.toUpperCase().includes(key)) {
                cropKey = key;
                break;
            }
        }
        
        if (!cropKey) {
            return {
                status: 'unknown',
                message: 'Planting window information not available for this crop'
            };
        }
        
        const window = plantingWindows[cropKey];
        const inWindow = this.isInWindow(month, window.start, window.end);
        const isOptimal = month === window.optimal;
        
        return {
            status: isOptimal ? 'optimal' : (inWindow ? 'suitable' : 'outside'),
            window: window,
            message: this.getPlantingMessage(cropKey, month, window),
            isOptimal: isOptimal,
            inWindow: inWindow
        };
    },
    
    /**
     * Check if current month is in planting window
     */
    isInWindow: function(month, start, end) {
        if (start <= end) {
            return month >= start && month <= end;
        } else {
            // Window crosses year boundary (e.g., Nov-Jan)
            return month >= start || month <= end;
        }
    },
    
    /**
     * Get planting message
     */
    getPlantingMessage: function(cropName, month, window) {
        if (month === window.optimal) {
            return `🌱 OPTIMAL TIME! ${cropName} should be planted NOW for best results.`;
        } else if (this.isInWindow(month, window.start, window.end)) {
            return `✅ Suitable time for ${cropName} planting (Window: Month ${window.start}-${window.end})`;
        } else {
            const monthsUntil = this.getMonthsUntilWindow(month, window.start);
            if (monthsUntil > 0) {
                return `⏳ ${cropName} planting starts in ${monthsUntil} month(s). Prepare now!`;
            } else {
                return `❌ Outside planting window for ${cropName}. Next window: Month ${window.start}`;
            }
        }
    },
    
    /**
     * Calculate months until planting window
     */
    getMonthsUntilWindow: function(current, windowStart) {
        if (current < windowStart) {
            return windowStart - current;
        } else {
            return (12 - current) + windowStart;
        }
    },
    
    /**
     * Get contextual greeting based on time of day
     */
    getGreeting: function(language = 'en') {
        const dt = this.getCurrentDateTime();
        const hour = dt.hour;
        
        const greetings = {
            en: {
                morning: 'Good Morning',
                afternoon: 'Good Afternoon',
                evening: 'Good Evening'
            },
            sn: {
                morning: 'Mangwanani',
                afternoon: 'Masikati',
                evening: 'Manheru'
            },
            nd: {
                morning: 'Livukile',
                afternoon: 'Litshonile',
                evening: 'Lihambile'
            }
        };
        
        let timeOfDay;
        if (hour >= 5 && hour < 12) {
            timeOfDay = 'morning';
        } else if (hour >= 12 && hour < 17) {
            timeOfDay = 'afternoon';
        } else {
            timeOfDay = 'evening';
        }
        
        return greetings[language][timeOfDay];
    },
    
    /**
     * Get market day information
     */
    getMarketDayInfo: function(district) {
        const dt = this.getCurrentDateTime();
        const dayName = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'][dt.dayOfWeek];
        
        // Common market days in Zimbabwe
        const marketDays = {
            'Harare': ['Tuesday', 'Thursday', 'Saturday'],
            'Bulawayo': ['Wednesday', 'Saturday'],
            'Mutare': ['Thursday', 'Saturday'],
            'Gweru': ['Friday', 'Saturday'],
            // Add more districts as needed
            'default': ['Saturday'] // Most rural markets on Saturday
        };
        
        const districtMarketDays = marketDays[district] || marketDays['default'];
        const isMarketDay = districtMarketDays.includes(dayName);
        
        return {
            today: dayName,
            isMarketDay: isMarketDay,
            marketDays: districtMarketDays,
            message: isMarketDay 
                ? `📊 Today is market day in ${district}!` 
                : `📅 Next market day: ${this.getNextMarketDay(dt.dayOfWeek, districtMarketDays)}`
        };
    },
    
    /**
     * Get next market day
     */
    getNextMarketDay: function(currentDay, marketDays) {
        const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        
        for (let i = 1; i <= 7; i++) {
            const nextDayIndex = (currentDay + i) % 7;
            const nextDay = days[nextDayIndex];
            if (marketDays.includes(nextDay)) {
                return nextDay;
            }
        }
        
        return marketDays[0] || 'Saturday';
    },
    
    /**
     * Get rainfall status based on month
     */
    getRainfallExpectation: function() {
        const dt = this.getCurrentDateTime();
        const month = dt.month;
        
        // Zimbabwe rainfall patterns
        if (month >= 11 || month <= 2) {
            return {
                status: 'wet',
                amount: 'High (150-250mm/month)',
                message: '🌧️ Peak rainy season - expect frequent rainfall',
                advice: 'Monitor for waterlogging, ensure drainage, disease vigilance'
            };
        } else if (month === 3 || month === 4) {
            return {
                status: 'declining',
                amount: 'Moderate (50-150mm/month)',
                message: '🌤️ Rains declining - prepare for harvest',
                advice: 'Complete fertilizer applications, prepare for harvest'
            };
        } else if (month >= 5 && month <= 9) {
            return {
                status: 'dry',
                amount: 'Low (<20mm/month)',
                message: '☀️ Dry season - irrigation required',
                advice: 'Irrigation essential, livestock feeding programs, water conservation'
            };
        } else {
            return {
                status: 'starting',
                amount: 'Low-Moderate (20-100mm/month)',
                message: '🌱 First rains expected - prepare for planting',
                advice: 'Monitor first rains, prepare land, procure inputs'
            };
        }
    },
    
    /**
     * Generate contextual farm advice
     */
    getContextualAdvice: function(district = null, crop = null) {
        const season = this.getCurrentSeason();
        const rainfall = this.getRainfallExpectation();
        const greeting = this.getGreeting('en');
        
        let advice = {
            greeting: greeting,
            season: season.name,
            activities: season.activities,
            rainfall: rainfall.message,
            priority: []
        };
        
        // Add crop-specific advice if crop provided
        if (crop) {
            const plantingWindow = this.getPlantingWindow(crop);
            advice.planting = plantingWindow.message;
            
            if (plantingWindow.isOptimal) {
                advice.priority.push(`🌱 PLANT ${crop.toUpperCase()} NOW!`);
            }
        }
        
        // Add seasonal priorities
        if (season.season === 'rainy') {
            advice.priority.push('⚠️ Monitor for pests and diseases', '💧 Ensure proper drainage');
        } else if (season.season === 'dry') {
            advice.priority.push('💧 Implement irrigation', '🌾 Feed livestock adequately');
        }
        
        // Add market info if district provided
        if (district) {
            const marketInfo = this.getMarketDayInfo(district);
            advice.market = marketInfo.message;
        }
        
        return advice;
    },
    
    /**
     * Format date for display
     */
    formatDate: function(date = new Date()) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        return date.toLocaleDateString('en-US', options);
    },
    
    /**
     * Initialize and display date info on page
     */
    displayCurrentInfo: function(elementId) {
        const dt = this.getCurrentDateTime();
        const season = this.getCurrentSeason();
        const rainfall = this.getRainfallExpectation();
        
        const html = `
            <div style="padding: 16px; background: rgba(16, 185, 129, 0.1); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.3); margin-bottom: 24px;">
                <div style="font-weight: 700; color: var(--primary-light); margin-bottom: 8px;">
                    📅 ${this.formatDate(dt.date)}
                </div>
                <div style="color: var(--text-secondary); font-size: 0.95em; line-height: 1.7;">
                    <strong>Season:</strong> ${season.name} (${season.period})<br>
                    <strong>Rainfall:</strong> ${rainfall.message}<br>
                    <strong>Activities:</strong> ${season.activities.slice(0, 3).join(', ')}
                </div>
            </div>
        `;
        
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = html;
        }
        
        return html;
    }
};

// Export for use in HTML
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DateTimeIntelligence;
}
