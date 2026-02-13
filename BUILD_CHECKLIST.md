# Build Verification Checklist

Use this checklist to ensure your build is successful and complete.

## Pre-Build Checklist

- [ ] Python 3.8-3.11 installed
- [ ] PyTorch installed and working
- [ ] TotalSegmentor installed
- [ ] nnU-Net (nnunetv2) installed
- [ ] PyInstaller installed (>= 5.10.0)
- [ ] All other dependencies installed
- [ ] `pip install -e .` completed successfully
- [ ] `python lung_asp_cli.py --help` works

## Build Process Checklist

- [ ] `build_full.sh` (or `.bat`) executed
- [ ] No errors during PyInstaller build
- [ ] Build completed in < 20 minutes
- [ ] `dist/lung_asp/` directory created
- [ ] Executable file exists (`lung_asp` or `lung_asp.exe`)
- [ ] Package size is reasonable (2-4 GB)

## Post-Build Testing

- [ ] Executable runs: `./dist/lung_asp/lung_asp --help`
- [ ] Help text displays correctly
- [ ] Version command works: `--version`
- [ ] No immediate crashes or errors

## Functionality Testing

- [ ] Can read DICOM files
- [ ] Can read NIfTI files
- [ ] Segmentation runs without errors
- [ ] Radiomics features calculate correctly
- [ ] Output files are created
- [ ] QC visualizations generate (if enabled)

## Package Testing

- [ ] Create distribution archive (.tar.gz or .zip)
- [ ] Archive size is < 5 GB
- [ ] Can extract archive successfully
- [ ] Executable works after extraction
- [ ] Portable (no external dependencies needed)

## Documentation Checklist

- [ ] `BUILD_LOCAL.md` saved
- [ ] `QUICK_BUILD_GUIDE.md` saved
- [ ] `USER_GUIDE.md` available
- [ ] Build scripts saved (`build_full.sh`/`.bat`)
- [ ] `lung_asp.spec` saved
- [ ] All source files from `src/` directory included

## Distribution Checklist

- [ ] Package created successfully
- [ ] Tested on clean system (if possible)
- [ ] README or user guide included
- [ ] Version number documented
- [ ] Platform specified (Windows/Linux/macOS)

## Optional Advanced Testing

- [ ] TotalSegmentor integration works
- [ ] nnU-Net integration works
- [ ] GPU detection works (if CUDA available)
- [ ] Batch processing works
- [ ] All 32 radiomics features calculate
- [ ] QC overlays in all three planes
- [ ] Large files (>1GB) process successfully

## Troubleshooting Tests

If any issues:
- [ ] Check `build/lung_asp/warn-lung_asp.txt`
- [ ] Review `build/lung_asp/xref-lung_asp.html`
- [ ] Run with `--debug` flag
- [ ] Check Python version compatibility
- [ ] Verify all dependencies present

## Success Criteria

✅ Build is successful if:
- All items in "Pre-Build" are checked
- All items in "Build Process" are checked
- All items in "Post-Build Testing" are checked
- At least 3/6 items in "Functionality Testing" are checked

## Notes

Date Built: ___________
Python Version: ___________
Platform: ___________
Package Size: ___________
Build Time: ___________

Issues Encountered:
_________________________________
_________________________________
_________________________________

Solutions Applied:
_________________________________
_________________________________
_________________________________

## Final Status

- [ ] **BUILD SUCCESSFUL** - Ready for distribution
- [ ] **BUILD NEEDS WORK** - See notes above
