#
# This is a project Makefile. It is assumed the directory this Makefile resides in is a
# project subdirectory.
#

ifeq ("$(AUTOCHECK)","")
AUTOCHECK=autocheck
endif

git:
	git add .
	git commit -m "$(AUTOCHECK)"
	git push

