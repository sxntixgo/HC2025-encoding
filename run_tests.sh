#!/bin/bash

set -e

# Function to show usage
show_usage() {
    echo "Usage: $0 [test_name]"
    echo ""
    echo "Available tests:"
    echo "  all-white-qr   Run all white QR code tests"
    echo "  rgb-ascii      Run RGB ASCII tests"
    echo "  dtmf          Run DTMF audio tests"
    echo "  morse         Run Morse code tests"
    echo "  all           Run all tests (default)"
    echo ""
    echo "Examples:"
    echo "  $0              # Run all tests"
    echo "  $0 all          # Run all tests"
    echo "  $0 all-white-qr # Run only all white QR tests"
    echo "  $0 dtmf         # Run only DTMF tests"
    exit 1
}

# Parse command line arguments
TEST_NAME="${1:-all}"

# Validate test name
case "$TEST_NAME" in
    all-white-qr|rgb-ascii|dtmf|morse|all)
        ;;
    -h|--help|help)
        show_usage
        ;;
    *)
        echo "Error: Unknown test '$TEST_NAME'"
        echo ""
        show_usage
        ;;
esac

echo "=== CTF Encoding Challenges Test Suite ==="
echo "Running: $TEST_NAME"
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required but not found"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install test dependencies
echo "Installing test dependencies..."
pip install -r tests/requirements.txt
echo ""

# Change to tests directory
cd tests

# Function to run individual tests
run_all_white_qr() {
    echo "=== Testing 01-all-white-qr challenge ==="
    python3 -m pytest test_all_white_qr.py -v
    echo ""
}

run_rgb_ascii() {
    echo "=== Testing 02-rgb-ascii challenge ==="
    python3 -m pytest test_rgb_ascii.py -v
    echo ""
}

run_dtmf() {
    echo "=== Testing 03-dtmf challenge ==="
    python3 -m pytest test_dtmf.py -v
    echo ""
}

run_morse() {
    echo "=== Testing 04-morse challenge ==="
    python3 -m pytest test_morse.py -v
    echo ""
}

run_all() {
    run_all_white_qr
    run_rgb_ascii
    run_dtmf
    run_morse

    echo "=== Running all tests together ==="
    python3 -m pytest test_*.py -v
    echo ""
}

# Execute the requested test
case "$TEST_NAME" in
    all-white-qr)
        run_all_white_qr
        ;;
    rgb-ascii)
        run_rgb_ascii
        ;;
    dtmf)
        run_dtmf
        ;;
    morse)
        run_morse
        ;;
    all)
        run_all
        ;;
esac

echo "=== Test execution completed successfully! ==="