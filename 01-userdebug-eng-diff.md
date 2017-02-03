# Difference between userdebug user and eng

'''Makefile
//Build files and then package it into the rom formats
.PHONY: droidcore
droidcore: files \
    systemimage \
    $(INSTALLED_BOOTIMAGE_TARGET) \
    $(INSTALLED_RECOVERYIMAGE_TARGET) \
    $(INSTALLED_USERDATAIMAGE_TARGET) \
    $(INSTALLED_CACHEIMAGE_TARGET) \
    $(INSTALLED_VENDORIMAGE_TARGET) \
    $(INSTALLED_FILES_FILE) \
    $(INSTALLED_FILES_FILE_VENDOR)
'''
