c CLASS = A
c  
c  
c  This file is generated automatically by the setparams utility.
c  It sets the number of processors and the class of the NPB
c  in this directory. Do not modify it by hand.
c  
        integer problem_size, niter_default
        parameter (problem_size=64, niter_default=400)
        double precision dt_default
        parameter (dt_default = 0.0015d0)
        logical  convertdouble
        parameter (convertdouble = .false.)
        character compiletime*11
        parameter (compiletime='27 Jan 2026')
        character npbversion*3
        parameter (npbversion='3.4')
        character cs1*9
        parameter (cs1='nvfortran')
        character cs2*5
        parameter (cs2='$(FC)')
        character cs3*6
        parameter (cs3='(none)')
        character cs4*6
        parameter (cs4='(none)')
        character cs5*46
        parameter (cs5='-O3 -march=native -stdpar=multicore -Minfo=...')
        character cs6*9
        parameter (cs6='$(FFLAGS)')
        character cs7*6
        parameter (cs7='randi8')
