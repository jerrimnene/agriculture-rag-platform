-- ============================================
-- ZAIES Location Intelligence Database
-- Zimbabwe Agricultural Geography System
-- ============================================

-- Natural Regions Master Table
CREATE TABLE IF NOT EXISTS natural_regions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    rainfall_min_mm INTEGER,
    rainfall_max_mm INTEGER,
    characteristics TEXT,
    suitable_enterprises TEXT[],
    constraints TEXT[]
);

INSERT INTO natural_regions VALUES
('I', 'Natural Region I - Specialized and Diversified Farming', 
 'Eastern Highlands - highest and most reliable rainfall',
 1000, 1500,
 'Very high rainfall, cool temperatures, fertile soils, low disease pressure',
 ARRAY['Tea', 'Coffee', 'Deciduous fruit', 'Dairy', 'Forestry', 'Intensive horticulture', 'High-yield maize'],
 ARRAY['Limited area', 'Transport costs', 'Cold damage to some crops']),

('IIa', 'Natural Region IIa - Intensive Farming',
 'Mashonaland Plateau - good rainfall, reliable',
 800, 1000,
 'High and reliable rainfall, warm to cool temperatures, good soils',
 ARRAY['Tobacco', 'Maize', 'Cotton', 'Soybean', 'Groundnuts', 'Wheat', 'Horticulture', 'Intensive livestock'],
 ARRAY['Mid-season dry spells possible', 'Disease pressure in wet years']),

('IIb', 'Natural Region IIb - Intensive Farming',
 'Intermediate areas between IIa and III',
 700, 800,
 'Moderate to good rainfall, reliable but variable',
 ARRAY['Maize', 'Tobacco', 'Cotton', 'Groundnuts', 'Sorghum', 'Livestock'],
 ARRAY['Rainfall variability', 'Occasional droughts', 'Lower yields than IIa']),

('III', 'Natural Region III - Semi-Intensive Farming',
 'Middleveld - moderate rainfall',
 650, 800,
 'Moderate rainfall, subject to seasonal droughts, moderate soil fertility',
 ARRAY['Drought-resistant maize', 'Sorghum', 'Cotton', 'Sunflower', 'Livestock (cattle)', 'Small grains'],
 ARRAY['Frequent dry spells', 'Drought risk', 'Lower and more variable yields']),

('IV', 'Natural Region IV - Semi-Extensive Farming',
 'Lowveld - low and erratic rainfall',
 450, 650,
 'Low and erratic rainfall, high temperatures, frequent droughts, poor soils',
 ARRAY['Livestock (cattle, goats)', 'Drought-resistant crops', 'Sorghum', 'Millet', 'Sunflower'],
 ARRAY['High drought risk', 'Poor soil fertility', 'Heat stress', 'Limited crop options']),

('V', 'Natural Region V - Extensive Farming',
 'Lowveld - very low rainfall',
 0, 450,
 'Very low and erratic rainfall, very high temperatures, severe droughts, poor soils',
 ARRAY['Extensive livestock (cattle, goats)', 'Wildlife ranching', 'Drought-resistant perennials'],
 ARRAY['Severe drought risk', 'Very poor soils', 'Crop production not viable', 'Water scarcity']);

-- ============================================
-- Provinces and Districts with Natural Regions
-- ============================================

CREATE TABLE IF NOT EXISTS districts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    province TEXT NOT NULL,
    district TEXT NOT NULL,
    natural_region TEXT REFERENCES natural_regions(id),
    secondary_region TEXT REFERENCES natural_regions(id), -- Some districts span multiple regions
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6),
    population INTEGER,
    farming_households INTEGER,
    main_crops TEXT[],
    main_livestock TEXT[],
    markets TEXT[],
    extension_offices INTEGER,
    research_stations TEXT[]
);

-- MASHONALAND CENTRAL
INSERT INTO districts (province, district, natural_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Mashonaland Central', 'Bindura', 'IIa', -17.3000, 31.3167, ARRAY['tobacco', 'maize', 'soybean'], ARRAY['cattle', 'poultry'], ARRAY['Bindura town market']),
('Mashonaland Central', 'Guruve', 'III', -16.6500, 30.7000, ARRAY['cotton', 'maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Guruve market']),
('Mashonaland Central', 'Centenary', 'IIb', -16.8000, 31.1167, ARRAY['tobacco', 'maize', 'cotton'], ARRAY['cattle'], ARRAY['Centenary market']),
('Mashonaland Central', 'Mazowe', 'IIa', -17.5167, 30.9667, ARRAY['tobacco', 'maize', 'horticulture'], ARRAY['cattle', 'poultry'], ARRAY['Mazowe market', 'Concession']),
('Mashonaland Central', 'Mount Darwin', 'III', -16.7833, 31.5833, ARRAY['maize', 'cotton', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Mount Darwin market']),
('Mashonaland Central', 'Rushinga', 'III', -16.6500, 32.0500, ARRAY['cotton', 'sorghum', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Rushinga market']),
('Mashonaland Central', 'Shamva', 'IIb', -17.3167, 31.5667, ARRAY['maize', 'tobacco', 'groundnuts'], ARRAY['cattle'], ARRAY['Shamva town market']),
('Mashonaland Central', 'Mbire', 'IV', -16.0000, 30.5000, ARRAY['sorghum', 'millet', 'cotton'], ARRAY['cattle', 'goats'], ARRAY['Mbire market']);

-- MASHONALAND EAST
INSERT INTO districts (province, district, natural_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Mashonaland East', 'Marondera', 'IIa', -18.1833, 31.5500, ARRAY['tobacco', 'maize', 'horticulture'], ARRAY['cattle', 'poultry', 'pigs'], ARRAY['Marondera town market', 'Ruwa market']),
('Mashonaland East', 'Mudzi', 'III', -16.9833, 32.5833, ARRAY['maize', 'sorghum', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Mudzi market']),
('Mashonaland East', 'Mutoko', 'IIb', -17.3833, 32.2167, ARRAY['maize', 'groundnuts', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Mutoko town market', 'Nyamapanda']),
('Mashonaland East', 'Chikomba', 'IIa', -18.9667, 30.9000, ARRAY['maize', 'tobacco', 'cotton'], ARRAY['cattle'], ARRAY['Chivhu market']),
('Mashonaland East', 'Goromonzi', 'IIa', -17.8500, 31.4500, ARRAY['tobacco', 'maize', 'horticulture'], ARRAY['cattle', 'poultry'], ARRAY['Ruwa market', 'Goromonzi']),
('Mashonaland East', 'Hwedza', 'IIb', -18.6167, 31.5667, ARRAY['maize', 'cotton', 'groundnuts'], ARRAY['cattle'], ARRAY['Hwedza market']),
('Mashonaland East', 'Seke', 'IIa', -17.9667, 31.1833, ARRAY['maize', 'horticulture', 'tobacco'], ARRAY['poultry', 'cattle'], ARRAY['Chitungwiza market']),
('Mashonaland East', 'Wedza', 'IIb', -18.5833, 31.5500, ARRAY['maize', 'cotton', 'sorghum'], ARRAY['cattle'], ARRAY['Wedza market']),
('Mashonaland East', 'UMP', 'IIb', -17.7000, 32.3000, ARRAY['maize', 'cotton', 'tobacco'], ARRAY['cattle'], ARRAY['UMP market']);

-- MASHONALAND WEST
INSERT INTO districts (province, district, natural_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Mashonaland West', 'Chinhoyi', 'IIa', -17.3667, 30.1833, ARRAY['tobacco', 'maize', 'soybean'], ARRAY['cattle', 'poultry'], ARRAY['Chinhoyi town market']),
('Mashonaland West', 'Hurungwe', 'III', -16.5000, 29.5000, ARRAY['cotton', 'maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Karoi market', 'Magunje']),
('Mashonaland West', 'Kariba', 'IV', -16.5167, 28.8000, ARRAY['cotton', 'sorghum'], ARRAY['cattle', 'goats', 'fish'], ARRAY['Kariba town market']),
('Mashonaland West', 'Makonde', 'IIa', -17.0833, 30.3333, ARRAY['tobacco', 'maize', 'cotton'], ARRAY['cattle'], ARRAY['Chinhoyi market']),
('Mashonaland West', 'Zvimba', 'IIa', -17.5000, 30.3333, ARRAY['tobacco', 'maize', 'horticulture'], ARRAY['cattle', 'poultry'], ARRAY['Banket market', 'Norton market']),
('Mashonaland West', 'Chegutu', 'IIa', -18.1333, 30.1500, ARRAY['tobacco', 'maize', 'cotton'], ARRAY['cattle'], ARRAY['Chegutu town market']);

-- MANICALAND
INSERT INTO districts (province, district, natural_region, secondary_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Manicaland', 'Mutare', 'I', 'IIa', -18.9667, 32.6500, ARRAY['tea', 'coffee', 'bananas', 'maize', 'horticulture'], ARRAY['dairy', 'poultry'], ARRAY['Mutare Mbare market', 'Sakubva market']),
('Manicaland', 'Nyanga', 'I', NULL, -18.2167, 32.7500, ARRAY['potatoes', 'deciduous fruit', 'maize', 'wheat'], ARRAY['dairy', 'trout'], ARRAY['Nyanga market']),
('Manicaland', 'Chimanimani', 'I', 'IIa', -19.8000, 32.8667, ARRAY['tea', 'coffee', 'bananas', 'timber'], ARRAY['cattle'], ARRAY['Chimanimani market']),
('Manicaland', 'Chipinge', 'IIa', 'III', -20.1833, 32.6167, ARRAY['coffee', 'tea', 'bananas', 'cotton', 'maize'], ARRAY['cattle'], ARRAY['Chipinge town market']),
('Manicaland', 'Buhera', 'III', 'IV', -19.3000, 31.6667, ARRAY['cotton', 'maize', 'sorghum', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Murambinda market', 'Birchenough Bridge']),
('Manicaland', 'Makoni', 'IIa', NULL, -18.6667, 32.0000, ARRAY['tobacco', 'maize', 'cotton'], ARRAY['cattle'], ARRAY['Rusape town market']),
('Manicaland', 'Mutasa', 'I', 'IIa', -18.6333, 32.6833, ARRAY['tea', 'coffee', 'timber', 'maize'], ARRAY['dairy'], ARRAY['Hauna market', 'Honde Valley']);

-- MASVINGO
INSERT INTO districts (province, district, natural_region, secondary_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Masvingo', 'Masvingo', 'IV', 'III', -20.0667, 30.8333, ARRAY['maize', 'sorghum', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Mucheke market', 'Masvingo town']),
('Masvingo', 'Chiredzi', 'V', 'IV', -21.0500, 31.6667, ARRAY['sugarcane', 'cotton', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Chiredzi market', 'Triangle']),
('Masvingo', 'Bikita', 'IV', NULL, -20.0667, 31.5667, ARRAY['cotton', 'sorghum', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Bikita market']),
('Masvingo', 'Chivi', 'IV', 'V', -20.5167, 30.9000, ARRAY['sorghum', 'millet', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Chivi market']),
('Masvingo', 'Gutu', 'IV', NULL, -19.6500, 31.1667, ARRAY['cotton', 'maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Gutu market', 'Mpandawana']),
('Masvingo', 'Mwenezi', 'V', NULL, -21.5167, 30.9833, ARRAY['sorghum', 'millet', 'livestock'], ARRAY['cattle', 'goats'], ARRAY['Mwenezi market', 'Rutenga']),
('Masvingo', 'Zaka', 'IV', NULL, -20.3667, 31.6000, ARRAY['cotton', 'maize', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Jerera market']);

-- MATABELELAND NORTH
INSERT INTO districts (province, district, natural_region, secondary_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Matabeleland North', 'Bulawayo', 'III', 'IV', -20.1500, 28.5833, ARRAY['maize', 'horticulture'], ARRAY['cattle', 'poultry'], ARRAY['Bulawayo markets']),
('Matabeleland North', 'Binga', 'IV', 'V', -17.6167, 27.3333, ARRAY['sorghum', 'millet', 'cotton'], ARRAY['cattle', 'goats', 'fish'], ARRAY['Binga market']),
('Matabeleland North', 'Bubi', 'III', 'IV', -19.3667, 28.5833, ARRAY['maize', 'sorghum', 'cattle'], ARRAY['cattle', 'goats'], ARRAY['Inyathi market']),
('Matabeleland North', 'Hwange', 'IV', 'V', -18.3667, 26.5000, ARRAY['cotton', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Hwange town market']),
('Matabeleland North', 'Lupane', 'IV', NULL, -18.9333, 27.8167, ARRAY['sorghum', 'cotton', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Lupane market']),
('Matabeleland North', 'Nkayi', 'IV', NULL, -19.0333, 28.8667, ARRAY['cotton', 'sorghum', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Nkayi market']),
('Matabeleland North', 'Tsholotsho', 'IV', 'V', -19.7667, 27.7500, ARRAY['sorghum', 'cotton'], ARRAY['cattle', 'goats'], ARRAY['Tsholotsho market']),
('Matabeleland North', 'Umguza', 'III', NULL, -19.6333, 28.7500, ARRAY['maize', 'cotton'], ARRAY['cattle'], ARRAY['Umguza market']);

-- MATABELELAND SOUTH
INSERT INTO districts (province, district, natural_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Matabeleland South', 'Gwanda', 'IV', -20.9333, 29.0167, ARRAY['sorghum', 'cotton', 'sunflower'], ARRAY['cattle', 'goats'], ARRAY['Gwanda town market']),
('Matabeleland South', 'Beitbridge', 'V', -22.2167, 30.0000, ARRAY['livestock production'], ARRAY['cattle', 'goats'], ARRAY['Beitbridge market']),
('Matabeleland South', 'Bulilima', 'IV', 'V', -20.6000, 27.5167, ARRAY['sorghum', 'millet'], ARRAY['cattle', 'goats'], ARRAY['Plumtree market']),
('Matabeleland South', 'Insiza', 'IV', -20.2833, 29.2667, ARRAY['cotton', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Filabusi market']),
('Matabeleland South', 'Mangwe', 'IV', 'V', -20.5667, 27.8333, ARRAY['sorghum', 'livestock'], ARRAY['cattle', 'goats'], ARRAY['Mangwe market']),
('Matabeleland South', 'Matobo', 'IV', -20.4500, 28.5000, ARRAY['maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Kezi market']),
('Matabeleland South', 'Umzingwane', 'III', 'IV', -20.3500, 28.8833, ARRAY['maize', 'cotton', 'sorghum'], ARRAY['cattle'], ARRAY['Esigodini market']);

-- MIDLANDS
INSERT INTO districts (province, district, natural_region, secondary_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Midlands', 'Gweru', 'III', 'IIb', -19.4500, 29.8167, ARRAY['maize', 'cotton', 'sorghum'], ARRAY['cattle', 'poultry'], ARRAY['Gweru markets']),
('Midlands', 'Chirumhanzu', 'III', NULL, -19.2500, 30.1667, ARRAY['maize', 'cotton'], ARRAY['cattle'], ARRAY['Mvuma market']),
('Midlands', 'Gokwe North', 'III', NULL, -17.9333, 28.9333, ARRAY['cotton', 'maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Gokwe Centre']),
('Midlands', 'Gokwe South', 'III', 'IV', -18.2167, 28.9333, ARRAY['cotton', 'maize', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Gokwe South market']),
('Midlands', 'Kwekwe', 'IIb', 'III', -18.9333, 29.8167, ARRAY['maize', 'tobacco', 'cotton'], ARRAY['cattle'], ARRAY['Kwekwe town market']),
('Midlands', 'Mberengwa', 'IV', NULL, -20.4833, 30.0500, ARRAY['sorghum', 'cotton', 'groundnuts'], ARRAY['cattle', 'goats'], ARRAY['Mberengwa market']),
('Midlands', 'Shurugwi', 'IV', 'III', -19.6667, 30.0000, ARRAY['maize', 'cotton', 'sorghum'], ARRAY['cattle'], ARRAY['Shurugwi town market']),
('Midlands', 'Zvishavane', 'IV', NULL, -20.3333, 30.0500, ARRAY['cotton', 'sorghum'], ARRAY['cattle', 'goats'], ARRAY['Zvishavane town market']);

-- HARARE (Metropolitan)
INSERT INTO districts (province, district, natural_region, latitude, longitude, main_crops, main_livestock, markets) VALUES
('Harare', 'Harare', 'IIa', -17.8292, 31.0522, ARRAY['horticulture', 'maize'], ARRAY['poultry', 'pigs'], ARRAY['Mbare Musika', 'Gazaland', 'Highfield']);

COMMIT;
