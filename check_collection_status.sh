#!/bin/bash
# Monitor data collection progress in real-time

echo "=========================================="
echo "LAP Coffee Data Collection Monitor"
echo "=========================================="
echo ""

# Check if processes are running
NDVI_PID=$(ps aux | grep "add_ndvi.py" | grep -v grep | awk '{print $2}')
NIGHTLIGHTS_PID=$(ps aux | grep "add_nightlights_daily.py" | grep -v grep | awk '{print $2}')

if [ -z "$NDVI_PID" ] && [ -z "$NIGHTLIGHTS_PID" ]; then
    echo "✅ All collection processes have completed!"
    echo ""
    echo "Output files:"
    ls -lh data/processed/*_multi_year.gpkg 2>/dev/null || echo "  (No files found yet)"
    exit 0
fi

echo "📊 Active Processes:"
echo "----------------------------------------"

if [ ! -z "$NDVI_PID" ]; then
    CPU_TIME=$(ps -p $NDVI_PID -o cputime= | tr -d ' ')
    echo "✓ NDVI Collection (PID: $NDVI_PID)"
    echo "  CPU Time: $CPU_TIME"
    echo "  Log: logs/ndvi_*.log"

    # Show last line of log if available
    LAST_LINE=$(find logs -name "ndvi_*.log" -exec tail -1 {} \; 2>/dev/null)
    if [ ! -z "$LAST_LINE" ]; then
        echo "  Status: $LAST_LINE"
    fi
    echo ""
fi

if [ ! -z "$NIGHTLIGHTS_PID" ]; then
    CPU_TIME=$(ps -p $NIGHTLIGHTS_PID -o cputime= | tr -d ' ')
    echo "✓ Nightlights Collection (PID: $NIGHTLIGHTS_PID)"
    echo "  CPU Time: $CPU_TIME"
    echo "  Log: logs/nightlights_*.log"

    # Show last line of log if available
    LAST_LINE=$(find logs -name "nightlights_*.log" -exec tail -1 {} \; 2>/dev/null)
    if [ ! -z "$LAST_LINE" ]; then
        echo "  Status: $LAST_LINE"
    fi
    echo ""
fi

echo "=========================================="
echo ""
echo "Estimated completion:"
echo "  NDVI: ~2-3 hours total"
echo "  Nightlights: ~1 hour total"
echo ""
echo "Run this script again to check progress:"
echo "  ./check_collection_status.sh"
