#!/bin/bash
# Check ingestion progress

echo "========================================"
echo "Ingestion Progress Monitor"
echo "========================================"

# Check if process is running
if ps aux | grep "[p]ython scripts/full_ingestion.py" > /dev/null; then
    echo "✅ Status: RUNNING"
    
    # Get process info
    ps aux | grep "[p]ython scripts/full_ingestion.py" | awk '{print "   PID:", $2, "| CPU:", $3"% | Memory:", $4"% | Time:", $10}'
    
    echo ""
    echo "📊 Current Progress:"
    grep "Processing documents:" ingestion_full.log 2>/dev/null | tail -1 | sed 's/.*Processing documents:/   /'
    
    echo ""
    echo "📄 Last file processed:"
    grep "Processing:" ingestion_full.log 2>/dev/null | tail -1 | sed 's/.*Processing:/   /'
    
    echo ""
    echo "🗺️  Last districts found:"
    grep "Districts found:" ingestion_full.log 2>/dev/null | tail -1 | sed 's/.*Districts found:/   /'
    
    echo ""
    echo "Log file: ingestion_full.log"
    echo "To view live: tail -f ingestion_full.log"
else
    echo "❌ Status: NOT RUNNING"
    
    # Check if completed successfully
    if grep -q "INGESTION COMPLETE" ingestion_full.log 2>/dev/null; then
        echo "✅ Ingestion completed successfully!"
        echo ""
        grep -A 10 "INGESTION COMPLETE" ingestion_full.log | grep -E "Total Time:|Documents after:|Districts covered:|Provinces covered:"
    elif grep -q "Error\|Failed" ingestion_full.log 2>/dev/null; then
        echo "⚠️  Ingestion failed. Check ingestion_full.log for errors"
        echo "Last error:"
        grep -i "error" ingestion_full.log | tail -3
    else
        echo "Process may have been interrupted"
    fi
fi

echo "========================================"
