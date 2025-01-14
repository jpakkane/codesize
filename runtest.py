#!/usr/bin/env python3

# SPDX-License-Identifier: Apache-2.0
# Copyright 2025 Jussi Pakkanen

import os, sys, subprocess, shutil, pathlib
import time

opt = (('O1', ['-Doptimization=1']),
       ('O2', ['-Doptimization=2']),
       ('O3', ['-Doptimization=3']),
       ('Os', ['-Doptimization=s']),
       )
lto = (('nolto', ['-Db_lto=false']),
        ('lto', ['-Db_lto=true'])
       )
rtti = (('nortti', ['-Dcpp_rtti=false']),
        ('rtti', ['-Dcpp_rtti=true'])
       )
exc = (('noexc', ['-Dcpp_eh=none']),
        ('exc', ['-Dcpp_eh=default'])
       )
ndbg = (('nondbg', ['-Db_ndebug=false']),
        ('ndbg', ['-Db_ndebug=true'])
        )



all_choices = [opt, lto, rtti, exc, ndbg]

class Measure:
    def __init__(self):
        self.srcdir = pathlib.Path('capypdf')
        self.builddir = pathlib.Path('build')
        self.buildtype = '--buildtype=debugoptimized'
        self.meson = '/home/jpakkane/workspace/meson/meson.py'
        self.libfile = self.builddir / 'src/libcapypdf.so.0.15.0'
        self.benchmark = self.builddir / 'benchmark/loremipsum'
        self.measurements = []

    def run(self):
        if self.builddir.exists():
            shutil.rmtree(self.builddir)
        subprocess.check_call([self.meson,
                               'setup',
                               self.buildtype,
                               self.srcdir,
                               self.builddir]
                               )
        idpieces = []
        setupargs = []
        self.recursive_do(idpieces, setupargs, all_choices)

    def recursive_do(self, idpieces, setupargs, optlist):
        if not optlist:
            idstr = '-'.join(idpieces)
            self.build_and_measure(idstr, setupargs)
        else:
            cur = optlist[0]
            optlist = optlist[1:]
            for idpiece, args in cur:
                self.recursive_do(idpieces + [idpiece],
                                  setupargs + args,
                                  optlist)

    def print_results(self):
        for idstr, libsize, runtime in self.measurements:
            print(idstr, libsize, runtime)

    def build_and_measure(self, idstr, args):
        subprocess.check_call([self.meson,
                               'configure',
                               self.builddir] + args)
        subprocess.check_call(['ninja', '-C', self.builddir])
        runtime = self.measure_time()
        libsize = self.get_libsize()
        self.measurements.append((idstr, libsize, runtime))

    def measure_time(self):
        starttime = time.time()
        subprocess.check_call([self.benchmark,
                               '100'
                               ])
        endtime = time.time()
        return endtime - starttime

    def get_libsize(self):
        subprocess.check_call(['strip', self.libfile])
        return self.libfile.stat().st_size

if __name__ == '__main__':
    m = Measure()
    m.run()
    m.print_results()

