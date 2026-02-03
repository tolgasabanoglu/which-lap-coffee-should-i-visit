#!/bin/bash

echo "Collecting Autumn 2024 data (Sep-Nov)"
echo "Expected time: ~1-2 hours"
echo ""

cd /Users/tolgasabanoglu/Desktop/github/which-lap-coffee-should-i-visit
source venv/bin/activate

# Create logs directory
mkdir -p logs

# Run collections in parallel
echo "Starting parallel data collection..."
python src/features/add_weather.py > logs/weather_autumn_$(date +%Y%m%d_%H%M%S).log 2>&1 &
WEATHER_PID=$!

python src/features/add_ndvi.py > logs/ndvi_autumn_$(date +%Y%m%d_%H%M%S).log 2>&1 &
NDVI_PID=$!

python src/features/add_nightlights_daily.py > logs/nightlights_autumn_$(date +%Y%m%d_%H%M%S).log 2>&1 &
NIGHTLIGHTS_PID=$!

echo "Weather PID: $WEATHER_PID"
echo "NDVI PID: $NDVI_PID"
echo "Nightlights PID: $NIGHTLIGHTS_PID"
echo ""
echo "Monitor progress with: ps -p $WEATHER_PID,$NDVI_PID,$NIGHTLIGHTS_PID"
