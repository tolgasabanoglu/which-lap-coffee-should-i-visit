#!/bin/bash
# Parallel data collection for LAP Coffee full-year dataset
# Runs weather, NDVI, and nightlights collection simultaneously

set -e  # Exit on error

echo "=========================================="
echo "LAP Coffee Full-Year Data Collection"
echo "=========================================="
echo ""
echo "Collecting 2024 data for:"
echo "  - Winter (Dec-Feb): 91 days"
echo "  - Spring (Mar-May): 92 days"
echo "  - Summer (Jun-Aug): 92 days"
echo "  (Autumn already collected, skipping)"
echo ""
echo "Total: 275 days × 16 cafés = ~4,400 new observations"
echo ""
echo "Running in parallel for maximum speed..."
echo "=========================================="
echo ""

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Create logs directory
mkdir -p logs

# Get start time
START_TIME=$(date +%s)

# Run all three scripts in parallel
echo "Starting parallel data collection..."
echo ""

python src/features/add_weather.py > logs/weather_$(date +%Y%m%d_%H%M%S).log 2>&1 &
WEATHER_PID=$!
echo "→ Weather API collection started (PID: $WEATHER_PID)"

python src/features/add_ndvi.py > logs/ndvi_$(date +%Y%m%d_%H%M%S).log 2>&1 &
NDVI_PID=$!
echo "→ NDVI (Google Earth Engine) collection started (PID: $NDVI_PID)"

python src/features/add_nightlights_daily.py > logs/nightlights_$(date +%Y%m%d_%H%M%S).log 2>&1 &
NIGHTLIGHTS_PID=$!
echo "→ Nightlights collection started (PID: $NIGHTLIGHTS_PID)"

echo ""
echo "All processes running in parallel..."
echo "You can monitor progress with:"
echo "  tail -f logs/weather_*.log"
echo "  tail -f logs/ndvi_*.log"
echo "  tail -f logs/nightlights_*.log"
echo ""

# Wait for all processes to complete
echo "Waiting for completion..."
wait $WEATHER_PID
WEATHER_STATUS=$?
echo "✓ Weather collection completed (status: $WEATHER_STATUS)"

wait $NDVI_PID
NDVI_STATUS=$?
echo "✓ NDVI collection completed (status: $NDVI_STATUS)"

wait $NIGHTLIGHTS_PID
NIGHTLIGHTS_STATUS=$?
echo "✓ Nightlights collection completed (status: $NIGHTLIGHTS_STATUS)"

# Calculate elapsed time
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "=========================================="
echo "Data Collection Complete!"
echo "=========================================="
echo "Total time: ${MINUTES}m ${SECONDS}s"
echo ""
echo "Output files created in data/processed/:"
echo "  - lap_locations_historical_weather_multi_year.gpkg"
echo "  - lap_locations_ndvi_daily_multi_year.gpkg"
echo "  - lap_locations_nightlights_monthly_multi_year.gpkg"
echo ""
echo "Next steps:"
echo "  1. Open prediction/analysis.ipynb notebook"
echo "  2. Run cells to merge data and upload to BigQuery"
echo "  3. Train the new RFC model"
echo ""

# Check if any process failed
if [ $WEATHER_STATUS -ne 0 ] || [ $NDVI_STATUS -ne 0 ] || [ $NIGHTLIGHTS_STATUS -ne 0 ]; then
    echo "⚠️  Warning: Some processes failed. Check logs for details."
    exit 1
fi

echo "✓ All processes completed successfully!"
