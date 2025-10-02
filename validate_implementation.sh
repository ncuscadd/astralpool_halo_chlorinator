#!/bin/bash
# Validation script for GPO implementation

echo "========================================"
echo "GPO Implementation Validation"
echo "========================================"
echo

# Check all required files exist
echo "Checking files..."
FILES=(
    "custom_components/astralpool_halo_chlorinator/gpo_helper.py"
    "custom_components/astralpool_halo_chlorinator/__init__.py"
    "custom_components/astralpool_halo_chlorinator/coordinator.py"
    "custom_components/astralpool_halo_chlorinator/select.py"
    "custom_components/astralpool_halo_chlorinator/sensor.py"
    "GPO_SUPPORT.md"
    "test_gpo.py"
    "IMPLEMENTATION_SUMMARY.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ✗ $file MISSING"
        exit 1
    fi
done

echo
echo "Checking Python syntax..."
python3 -m py_compile custom_components/astralpool_halo_chlorinator/gpo_helper.py
python3 -m py_compile custom_components/astralpool_halo_chlorinator/__init__.py
python3 -m py_compile custom_components/astralpool_halo_chlorinator/coordinator.py
python3 -m py_compile custom_components/astralpool_halo_chlorinator/select.py
python3 -m py_compile custom_components/astralpool_halo_chlorinator/sensor.py
echo "  ✓ All files compile successfully"

echo
echo "Running test script..."
python3 test_gpo.py
if [ $? -eq 0 ]; then
    echo "  ✓ Tests passed"
else
    echo "  ✗ Tests failed"
    exit 1
fi

echo
echo "Checking code style..."
black --check custom_components/astralpool_halo_chlorinator/gpo_helper.py \
              custom_components/astralpool_halo_chlorinator/__init__.py \
              custom_components/astralpool_halo_chlorinator/coordinator.py \
              custom_components/astralpool_halo_chlorinator/select.py \
              custom_components/astralpool_halo_chlorinator/sensor.py 2>&1 | grep -q "would be reformatted"
if [ $? -eq 1 ]; then
    echo "  ✓ Code formatting is correct"
else
    echo "  ✗ Code needs formatting"
    exit 1
fi

echo
echo "Checking linting..."
flake8 --max-line-length=88 --extend-ignore=E203,W503 \
       custom_components/astralpool_halo_chlorinator/gpo_helper.py \
       custom_components/astralpool_halo_chlorinator/__init__.py \
       custom_components/astralpool_halo_chlorinator/coordinator.py \
       custom_components/astralpool_halo_chlorinator/select.py \
       custom_components/astralpool_halo_chlorinator/sensor.py
if [ $? -eq 0 ]; then
    echo "  ✓ No linting issues"
else
    echo "  ✗ Linting issues found"
    exit 1
fi

echo
echo "========================================"
echo "✓ All validations passed!"
echo "========================================"
echo
echo "Implementation is ready for testing with a real device."
