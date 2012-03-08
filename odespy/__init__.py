"""
The ``odespy`` package contains tools for solving ordinary
differential equations (ODEs). The user specifies the problem through
high-level Python code. Both scalar ODEs and systems of ODEs are
supported.  A wide range of numerical methods for ODEs are offered:

"""

# Insert tutorial from ../doc/src/odespy/odespy.rst

__tutorial__ = r'''
Basic Usage
===========

Overview
--------

The typical usage of the tools consists of six steps. These are
outlined in generic form below.

Step 1
~~~~~~

Write the ODE problem on the generic form :math:`u' = f(u, t)`,
where :math:`u(t)` is the unknown function to be solved for, or a vector
of unknown functions of time in case of a system of ODEs.

Step 2
~~~~~~

Implement the right-hand side function :math:`f(u, t)`, which
defines the ODEs to be solved, as a Python function ``f(u, t)``.  The
argument ``u`` is either a ``float`` object (in case of a scalar ODE) or a
``numpy`` array object (in case of a system of ODEs).  Alternatively, a
class with a ``__call__`` method can be used instead of a plain
function.  Some tools in this package also allow implementation of :math:`f`
in Fortran or C for increased efficiency.

Step 3
~~~~~~

Create a method object

.. code-block:: python

        method = classname(f)

where ``classname`` is the name of a class in this package implementing
the desired numerical method.

Many solver classes has a range of parameters that the user can set to
control various parts of the solution process. The parameters are
documented in the doc string of the class (``pydoc classname`` will list
the documentation in a terminal window). One can either specify parameters
at construction time, via extra keyword arguments to the constructor,

.. code-block:: python

        method = classname(f, prm1=value1, prm2=value2, ...)

or at any time using the ``set`` method:

.. code-block:: python

        method.set(prm1=value1, prm2=value2, prm3=value3)
        ...
        method.set(prm4=value4)


Step 4
~~~~~~

Set the initial condition, :math:`u(0)=U_0`,

.. code-block:: python

        method.set_initial_condition(U0)

where ``U0`` is either a number, for a scalar ODE, or a sequence (list, tuple,
``numpy`` array), for a system of ODEs.

Step 5
~~~~~~

Solve the ODE problem, which means to compute :math:`u(t)` at
some discrete user-specified time points :math:`t_i`, for
:math:`i=0,1,\ldots,n`.

.. code-block:: python

        T = ...  # end time
        time_points = numpy.linspace(0, T, n+1)
        u, t = method.solve(time_points)

In case of a scalar ODE, the returned solution ``u`` is a one-dimensional
``numpy`` array where ``u[i]`` holds the solution at time point ``t[i]``.
For a system of ODEs, the returned ``u`` is a two-dimensional ``numpy``
array where ``u[i,j]`` holds the solution of the $j$-th unknown
function at the $i$-th time point ``t[i]`` (:math:`u_j(t_i)` in mathematics
notation).

The ``time_points`` array specifies the time points where we want the
solution to be computed. The returned array ``t`` is the same as
``time_points``.  The simplest numerical methods in the ``odespy``
package apply the ``time_points`` array directly in the solution. That
is, the time steps used are given by ``time_points[i] -
time_points[i-1]``, for ``i=0,1,...,len(time_points)-1``.  Some more
advanced adaptive methods compute the time steps internally. Then the
``time_points`` array is just a specification of the time points where
we want to know the solution.

(**hpl**: Need to document how the tp array is used.)

(**hpl**: Need to comment on storage.)

The ``solve`` method in solver classes also allows a second argument,
``terminate``, which is a user-implemented Python function specifying
when the solution process is to be terminated. For example,
terminating when the solution reaches an asymptotic (known) value
``a`` can be done by

.. code-block:: python

        def terminate(u, t, step_no):
            # u and t are arrays. Most recent solution is u[step_no].
            tolerance = 1E-6
            return True if abs(u[step_no] - a) < tolerance else False

        u, t = method.solve(time_points, terminate)

The arguments transferred to the ``terminate`` function are the
solution array ``u``, the corresponding time points ``t``, and
an integer ``step_no`` reflecting the most recently computed ``u``
value. That is, ``u[step_no]`` is most recently computed value of :math:`u`.
(The array data ``u[step_no+1:]`` will typically be zero as these
are uncomputed future values.)


Step 6
~~~~~~

Extract solution components for plotting and further analysis.
Since the ``u`` array returned from ``method.solve`` stores all unknown
functions at all discrete time levels, one usually wants to extract
individual unknowns as one-dimensional arrays. Here is an example
where unknown :math:`0` and :math:`k` are extracted in individual arrays and plotted:

.. code-block:: python

        u_0 = u[:,0]
        u_k = u[:,k]

        from matplotlib.pyplot import plot, show
        plot(t, u_0, t, u_k)
        show()


.. _ode:sec:exgr:

Example: Exponential Growth
---------------------------

Our first example concerns the simple scalar ODE problem :math:`u'=cu`,
:math:`u(0)=A`, where :math:`A>0` and :math:`c>0` are known constants. Using a standard
Runge-Kutta method of order four, the code for solving the problem in
the time interval :math:`[0,10]`, with :math:`N=30` time steps, looks like this:


.. code-block:: python

        c = 0.1
        A = 1.5

        def f(u, t):
            return c*u

        import odespy
        method = odespy.RK4(f)
        method.set_initial_condition(A)

        import numpy
        N = 30  # no of time steps
        time_points = numpy.linspace(0, 10, N+1)
        u, t = method.solve(time_points)

        from matplotlib.pyplot import *
        plot(t, u)
        show()


With the ``RK4`` method and other non-adaptive methods
the time steps are dictated by the ``time_points`` array.
A constant time step of size ``time_points[1] - time_points[0] = 1/3``
is implied in the present example.


.. _ode:sec:exgr:farg:

Parameters in the Right-Hand Side Function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The right-hand side function and all physical parameters are often
lumped together in a class, for instance,


.. code-block:: python

        class ExponentialGrowth:
            def __init__(self, c=1, A=1):
                self.c, self.A = c, A

            def __call__(self, u, t):
                return self.c*u

        f = ExponentialGrowth(c=0.1, A=1.5)

        import odespy
        method = odespy.RK4(f)
        method.set_initial_condition(f.A)


We may also compare the numerical and exact solution:


.. code-block:: python

        u_exact = f.A*numpy.exp(f.c*t)
        error = numpy.abs(u_exact - u).max()
        print 'Max deviation of numerical solution:', error

        from matplotlib.pyplot import *
        plot(t, u, 'r-', t, u_exact, 'bo')
        legend(['RK4, N=%d' % N, 'exact'])
        show()


Instead of having the ``c`` variable as a global variable or
in a class, we may include it as an extra argument to ``f``, either
as a positional argument or as a keyword argument. Positional arguments
can be sent to ``f`` via the constructor argument ``f_args`` (a list/tuple of
variables), while a dictionary ``f_kwargs`` is used to transfer
keyword arguments to ``f`` via the constructor:


.. code-block:: python

        # f has extra positional argument
        def f(u, t, c):
            return c*u

        method = odespy.RK4(f, f_args=[c])

        # Alternative: f has extra keyword argument
        def f(u, t, c=1):
            return c*u

        method = odespy.RK4(f, f_kwargs={'c': c})


The right-hand side function ``f`` may feature both extra positional
arguments and extra keyword arguments,

.. code-block:: python

        def f(u, t, arg1, arg2, arg3, ..., kwarg1=val1, kwarg2=val2, ...):
            ...

        method = odespy.classname(f,
                            f_args=[arg1, arg2, arg3, ...],
                            f_kwargs=dict(kwarg1=val1, kwarg2=val2, ...))

        # Alternative setting of f_args and f_kwargs
        method.set(f_args=[arg1, arg2, arg3, ...],
                   f_kwargs=dict(kwarg1=val1, kwarg2=val2, ...))

Solvers will call ``f`` as ``f(u, t, *f_args, **f_kwargs)``.

Continuing a Previous Simulation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is easy to simulate for some time interval :math:`[0, T_1]`,
the continue with :math:`u(T_1)` as new initial condition and simulate for
:math:`t` in :math:`[T_1, T_2]` and so on. Let us divide the time
domain :math:`[0,10]` into subdomains and compute the solution for
each subdomain in sequence. The following program performs the steps.


.. code-block:: python

        c = 0.1
        A = 1.5

        def f(u, t):
            return c*u

        import odespy, numpy
        from matplotlib.pyplot import *

        method = odespy.RK4(f)

        # Split time domain into subdomains and
        # integrate the ODE in each subdomain
        T = [0, 1, 3, 6, 10, 20]

        N_tot = 30               # no of time intervals in total
        dt = float(T[-1])/N_tot  # time step, kept fixed
        u = []; t = []           # collectors for u and t

        for i in range(len(T)-1):
            T_interval = T[i+1] - T[i]
            N = int(round(T_interval/dt))
            time_points = numpy.linspace(T[i], T[i+1], N+1)

            method.set_initial_condition(A)  # at time_points[0]
            print 'Solving in [%s, %s] with %d intervals' % \
                  (T[i], T[i+1], N)
            ui, ti = method.solve(time_points)
            A = ui[-1]  # newest u is next initial condition

            plot(ti, ui)
            hold('on')

            u.append(ui);  t.append(ti)

        # Can concatenate all the elements of u and t, if desired
        u = numpy.concatenate(u);  t = numpy.concatenate(t)
        #plot(t, u, 'bo')  # same curve
        show()



Example: Decay Equation
-----------------------

The second example also concerns the ODE :math:`u'=cu`, but this time with
:math:`c<0`. We want to integrate until the asymptotic value :math:`u=0` is
reached with an accuracy of :math:`0.001`. For this purpose we need a
``terminate`` function, which returns ``True`` when the termination
criterion is met:


.. code-block:: python

        tol = 0.001  # tolerance for terminating the simulation

        def terminate(u, t, step_no):
            # Most recent solution is in u[step_no] at time t[step_no]
            if abs(u[step_no]) <= tol:
                return True
            else:
                return False


The complete program may take the form


.. code-block:: python

        c = -0.1
        A = 1.5

        def f(u, t):
            return c*u

        import odespy
        method = odespy.RK4(f)
        method.set_initial_condition(A)

        import numpy
        # Make sure integration interval [0, T] is large enough
        N = 50
        T = 150
        time_points = numpy.linspace(0, T, N+1)

        tol = 0.001  # tolerance for terminating the simulation

        def terminate(u, t, step_no):
            # Most recent solution is in u[step_no] at time t[step_no]
            if abs(u[step_no]) <= tol:
                return True
            else:
                return False

        u, t = method.solve(time_points, terminate)

        print "Solve u'=%g*u, u(0)=%g, for t in [%g, %g] and u>%g" % \
              (c, A, time_points[0], time_points[-1], tol)
        print 'Final u(t=%g)=%g after %d steps' % (t[-1], u[-1], len(u)-1)

        from matplotlib.pyplot import *
        print plot
        plot(t, u)
        show()


Note that the size of the returned arrays ``u`` and ``t`` fits
the time interval up to the point of termination by ``terminate``.


Example: Decay Equation with Other Symbols
------------------------------------------

The ``odespy`` package applies ``u`` for the unknown function or
vector of unknown functions and ``t`` as the name of the independent
variable. Many problems involve other symbols for functions and
independent variables. These symbols should be reflected in the code.
For example, here is a coding example involving the differential
equation :math:`y'(x)=-y(x)`, :math:`y(0)=1`:


.. code-block:: python

        def myrhs(y, x):
            return -y

        import odespy
        method = odespy.RK4(myrhs)
        method.set_initial_condition(1)

        import numpy
        # Make sure integration interval [0, L] is large enough
        N = 50
        L = 10
        x_points = numpy.linspace(0, L, N+1)

        def terminate(y, x, stepnumber):
            tol = 0.001
            return True if abs(y[stepnumber]) < tol else False

        y, x = method.solve(x_points, terminate)

        print 'Final y(x=%g)=%g' % (x[-1], y[-1])

        from matplotlib.pyplot import *
        plot(x, y)
        show()


As shown, we use ``y`` for ``u``, ``x`` for ``t``, and ``x_points`` instead
of ``time_points``.

Example: The Pendulum Equation
------------------------------

The angle :math:`\theta` of a pendulum with mass :math:`m` and length :math:`L`
is governed by the equation
(neglecting air resistance for simplicity)

.. math::

        mL\ddot\theta + mg\sin\theta = 0,\quad \theta (0)=\Theta,\
        \dot\theta (0)=0 .


A dot over :math:`\theta` implies differentiation with respect to time.
The ODE can be written as :math:`\ddot\theta + c\sin\theta=0` by
introducing :math:`c = g/L`.
This problem must be expressed as a first-order ODE system if it is
going to be solved by the tools in the ``odespy`` package.
Introducing :math:`\omega = \dot\theta` (the angular velocity) as auxiliary
unknown, we get the system

.. math::

        \dot\theta &= \omega,\\
        \dot\omega &= -c\sin\theta,


with :math:`\theta(0)=\Theta` and :math:`\omega(0)=0`.

Now the ``f`` function must return a list or array with the two
right-hand side functions:


.. code-block:: python

        def f(u, t):
            theta, omega = u
            return [omega, -c*sin(theta)]


Note that when we have a system of ODEs with ``n`` components, the ``u``
object sent to the ``f`` function is an array of length ``n``,
representing the value of all components in the ODE system at time ``t``.
Here we extract the two components of ``u`` in separate local variables
with names equal to what is used in the mathematical description of
the current problem.

The initial conditions must be specified as a list:


.. code-block:: python

        method = odespy.Heun(f)
        method.set_initial_condition([Theta, 0])


To specify the time points we here first decide on a number of periods
(oscillations back and forth) to simulate and then on the time resolution
of each period. (When :math:`\Theta` is small we can replace
:math:`\sin\theta` by :math:`\theta` and find an analytical
solution
:math:`\theta (t)=\Theta\cos\left(\sqrt{c}t\right)`
whose period is :math:`2\pi/\sqrt{c}`.)


.. code-block:: python

        freq = sqrt(c)      # frequency of oscillations when Theta is small
        period = 2*pi/freq  # the period of the oscillations
        T = 10*period        # final time
        N_per_period = 20   # resolution of one period
        N = N_per_period*period
        time_points = numpy.linspace(0, T, N+1)

        u, t = method.solve(time_points)


The ``u`` returned from ``method.solve`` is a two-dimensional array, where the
columns hold the various solution functions of the ODE system. That is,
the first column holds :math:`\theta` and the second column holds
:math:`\omega`. For convenience we extract the individual solution
components in individual arrays:


.. code-block:: python

        theta = u[:,0]
        omega = u[:,1]

        from matplotlib.pyplot import *
        theta_small = Theta*numpy.cos(sqrt(c)*t)
        plot(t, theta, 'r-', t, theta_small, 'y-')
        legend(['theta', 'small angle approximation'])
        savefig('tmp.png')
        show()


Looking at the plot reveals that the numerical solution has
an alarming feature: the amplitude grows (indicating increasing
energy in the system). Changing ``T`` to 28 periods instead of 10
makes the numerical solution explode.


.. figure:: figs-tut/exos1a.png
   :width: 500

   *Comparison of large-amplitude numerical solution with corresponding analytical solution (derived for small amplitudes)*


Changing solution method is a matter of substituting ``Heun`` by ``RK4``,
for instance:


.. code-block:: python

        method = odespy.RK4(f)


The amplitude is now correct, but the numerical solution has a different
frequency than the inaccurate analytical "solution".


.. figure:: figs-tut/exos1b.png
   :width: 500

   *Switching to a 4-th order Runge-Kutta method improves the numerical solution*


Changing :math:`\Theta` to a small value, say 0.05, makes the two curves
coincide. The next section shows how easy it is to run a problem with a set
of numerical methods.


Example: Testing Several Methods
--------------------------------

We shall now make a more advanced solver by
extending the previous example. More specifically, we shall

  * represent the right-hand side function as class,

  * compare several different solvers,

  * compute error of numerical solutions.

Since we want to compare numerical errors in the various
solvers we need a test problem where the exact solution is known.
Approximating :math:`\sin(\theta)` by :math:`\theta`
(valid for small :math:`\theta`), gives the ODE system

.. math::

        \dot\theta &= \omega,\\
        \dot\omega &= -c\theta,


with :math:`\theta(0)=\Theta` and :math:`\omega(0)=0`.

Right-hand side functions with parameters can be handled by
including extra arguments via the ``f_args`` and ``f_kwargs`` functionality,
or by using a class where the parameters are attributes and
a ``__call__`` method makes the class instance callable as a function. The section :ref:`ode:sec:exgr:farg` exemplifies the details.
A minimal class representation of the right-hand side
function in the present case looks like this:

.. code-block:: py


        class Problem:
            def __init__(self, c, Theta):
                self.c, self.Theta = float(c), float(Theta)

            def __call__(self, u, t):
                theta, omega = u;  c = self.c
                return [omega, -c*theta]

        problem = Problem(c=1, Theta=pi/4)

It would be convenient to add an attribute ``period`` which holds
an estimate of the period of oscillations as we need this for
deciding on the complete time interval for solving the differential
equations. An appropriate extension of class ``Problem`` is therefore


.. code-block:: python

        class Problem:
            def __init__(self, c, Theta):
                self.c, self.Theta = float(c), float(Theta)

                self.freq = sqrt(c)
                self.period = 2*pi/self.freq

            def __call__(self, u, t):
                theta, omega = u;  c = self.c
                return [omega, -c*theta]

        problem = Problem(c=1, Theta=pi/4)


The second extension is to loop over many solvers. All
solvers can be listed by

>>> import odespy, pprint
>>> solvers = list_all_solvers()
>>> for solver in solvers:
...   print solver
...
AdamsBashMoulton2
AdamsBashMoulton3
AdamsBashforth2
AdamsBashforth3
AdamsBashforth4
AdaptiveResidual
Backward2Step
BackwardEuler
BogackiShampine
CashKarp
Dop853
Dopri5
DormandPrince
Fehlberg
Euler
ForwardEuler
Heun
Leapfrog
LeapfrogFiltered
Lsoda
Lsodar
Lsode
Lsodes
Lsodi
Lsodis
Lsoibt
MidpointImplicit
MidpointIter
MyRungeKutta
MySolver
RKC
RKF45
RK2
RungeKutta2
RK3
RungeKutta3
RK4
RungeKutta4
RKFehlberg
SymPy_odefun
ThetaRule
Trapezoidal
Vode

A similar function, ``list_available_solvers``, returns a list of the
names of the solvers that are available in the current installation
(e.g., the ``Vode`` solver is only available if the comprehensive
``scipy`` package is installed).
This is the list that is usually most relevant.

For now we explicitly choose a subset of the commonly available solvers:


.. code-block:: python

        import odespy
        solvers = [
            odespy.ThetaRule(problem, theta=0),   # Forward Euler
            odespy.ThetaRule(problem, theta=0.5), # Midpoint
            odespy.ThetaRule(problem, theta=1),   # Backward Euler
            odespy.RK4(problem),
            odespy.MidpointIter(problem, max_iter=2, eps_iter=0.01),
            odespy.LeapfrogFiltered(problem),
            ]


It will be evident that the ``ThetaRule`` solver with ``theta=0`` and
``theta=1`` (Forward and Backward Euler methods) gives growing and
decaying amplitudes, respectively, while the other solvers are
capable of reproducing the constant amplitude of the oscillations of
in the current mathematical model.

The loop over the chosen solvers may look like


.. code-block:: python

        N_per_period = 20
        T = 3*problem.period   # final time
        import numpy
        import matplotlib.pyplot as mpl
        legends = []

        for method in solvers:
            method_name = str(method)
            print method_name

            method.set_initial_condition([problem.Theta, 0])
            N = N_per_period*problem.period
            time_points = numpy.linspace(0, T, N+1)

            u, t = method.solve(time_points)

            theta = u[:,0]
            legends.append(method_name)
            mpl.plot(t, theta)
            mpl.hold('on')
        mpl.legend(legends)
        mpl.savefig(__file__[:-3] + '.png')
        mpl.show()



.. figure:: figs-tut/exos2.png
   :width: 500

   *Comparison of solutions*


We can extend this program to compute the error in each numerical
solution for different time step sizes.
Let ``results`` be a dictionary with the method name as
key, containing two sub dictionaries ``dt`` and ``error``, which hold
a sequence of time steps and a sequence of corresponding
errors, respectively. The errors are computed by subtracting
the numerical solution from the exact solution,

.. code-block:: python

        theta_exact = lambda t: problem.Theta*numpy.cos(sqrt(problem.c)*t)
        u, t = method.solve(time_points)
        theta = u[:,0]
        error = numpy.abs(theta_exact(t) - theta)

The so-called L2 norm of the ``error`` array is a suitable
scalar error measure (square root of total error squared and integrated,
here numerically):

.. code-block:: python

        error_L2 = sqrt(numpy.sum(error**2)/dt)

where ``dt`` is the time step size.

Typical loops over solvers and resolutions look as follows:


.. code-block:: python

        T = num_periods*problem.period       # final time
        results = {}
        resolutions = [10, 20, 40, 80, 160]  # intervals per period
        import numpy

        for method in solvers:
            method_name = str(method)
            results[method_name] = {'dt': [], 'error': []}

            method.set_initial_condition([problem.Theta, 0])

            for N_per_period in resolutions:
                N = N_per_period*problem.period
                time_points = numpy.linspace(0, T, N+1)

                u, t = method.solve(time_points)

                theta = u[:,0]
                error = numpy.abs(theta_exact(t) - theta)
                error_L2 = sqrt(numpy.sum(error**2)/N)
                if not numpy.isnan(error_L2):  # drop nan
                    results[method_name]['dt'].append(t[1] - t[0])
                    results[method_name]['error'].append(error_L2)


Assuming the error to be of the form :math:`C\Delta t^r`, we can estimate
:math:`C` and :math:`r` from two consequtive experiments to obtain a sequence
of :math:`r` values which (hopefully) convergences to a value that we can
view as the empirical convergence rate of a method.
Given the sequence of time steps and errors, a function in
the ``scitools`` package automatically computes the sequence of
:math:`r` values:


.. code-block:: python

        # Analyze convergence
        from scitools.convergencerate import OneDiscretizationPrm
        pairwise_rates = OneDiscretizationPrm.pairwise_rates  # short form

        print '\n\nConvergence results for %d periods' % num_periods
        for method_name in results:
            rates, C = pairwise_rates(results[method_name]['dt'],
                                      results[method_name]['error'])
            rates = ', '.join(['%.1f' % rate for rate in rates])
            print '%-20s r: %s E_min=%.1E' % \
                  (method_name, rates, min(results[method_name]['error']))


With 4 periods we get

.. code-block:: python

        ThetaRule(theta=0)   r: 2.9, 1.9, 1.4, 1.2 E_min=1.1E-01
        RK2                  r: 2.1, 2.0, 2.0, 2.0 E_min=8.4E-04
        ThetaRule(theta=1)   r: 0.3, 0.5, 0.7, 0.8 E_min=9.0E-02
        RK4                  r: 4.0, 4.0, 4.0, 4.0 E_min=2.6E-08
        ThetaRule            r: 2.0, 2.0, 2.0, 2.0 E_min=4.2E-04
        Leapfrog             r: 2.1, 2.0, 2.0, 2.0 E_min=8.5E-04
        LeapfrogFiltered     r: 0.2, 0.4, 0.6, 0.8 E_min=1.3E-01

The rates of the Forward and Backward Euler methods (1st and 3rd line) have
not yet converged to unity, as expected, while the 2nd-order
Runge-Kutta method, Leapfrog, and the $\theta$|$theta$-rule with :math:`\theta =0.5`
(``ThetaRule`` with default value of ``theta``) shows the expected
:math:`r=2` value. The 4th-order Runge-Kutta holds the promise of being of 4th
order, while the filtered Leapfrog method has slow convergence and
a fairly large error, which is also evident in the previous figure.

Extending the time domain to 20 periods makes many of the
simplest methods inaccurate and the rates computed on coarse
time meshes are irrelevnat:

.. code-block:: python

        ThetaRule(theta=0)   r: 10.4, 22.0, 18.2, 10.4 E_min=3.3E+02
        RK2                  r: 51.4, 16.1, 2.3, 2.1 E_min=1.1E-01
        ThetaRule(theta=1)   r: 11.2, 0.0, 0.1 E_min=5.0E-01
        RK4                  r: 1.0, 3.6, 4.0, 4.0 E_min=8.2E-05
        ThetaRule            r: 87.8, 0.2, 1.7, 2.0 E_min=5.3E-02
        Leapfrog             r: 95.9, 18.0, 1.0, 2.0 E_min=1.1E-01
        LeapfrogFiltered     r: -0.0, 121.2, 0.3, 0.1 E_min=5.2E-01


Example: Solving a Stochastic Differential Equation
---------------------------------------------------

We consider an oscillator driven by stochastic white noise:

.. math::
         x''(t) + bx'(t) + cx(t) = N(t),\ x(0)=X,\ x'(0) =0,

where :math:`N(t)` is the white noise computed discretely as

.. math::
         N(t_i) \approx \sigma\frac{\Delta W_i}{\sqrt{t_{i+1}-t_i}},

where :math:`\Delta W_1,\Delta W_2,\ldots` are independent normally
distributed random variables with mean zero and unit standard
deviation, and :math:`\sigma` is the strength of the noise.
The idea is that :math:`N(t)` provides an excitation containing "all" frequencies,
but the oscillator is a strong filter: with low damping one of the
frequencies in :math:`N(t)` will hit the resonance frequency
:math:`\sqrt{c}/(2\pi)` which will
then dominate the output signal :math:`x(t)`.

The noise is additive in this stochastic differential equation so
there is no difference between the Ito and Stratonovich interpretations
of the equation.

The challenge with this model problem is that stochastic differential
equations do not fit with the user interface offered by ``odespy``,
since the right-hand side function is assumed to be dependent only
on the solution and the present time (``f(u,t)``), and additional
user-defined parameters, but for the present problem the right-hand
side function needs information about :math:`N(t)` and hence
the size of the current time step. We can solve this issue by
having a reference to the solver in the right-hand side function,
precomputing :math:`N(t_i)` for all time intervals :math:`i`, and using the ``n``
attribute in the solver for selecting the right force term (recall
that some methods will call the right-hand side function many times
during a time interval - all these calls must use the same value of
the white noise).

The right-hand side function must do many things so a class is
appropriate:


.. code-block:: python

        class WhiteNoiseOscillator:
            def __init__(self, b, c, sigma=1):
                self.b, self.c, self.sigma = b, c, sigma

            def connect_solver(self, solver):
                """Solver is needed for time step number and size."""
                self.solver = solver

            def __call__(self, u, t):
                if not hasattr(self, 'N'):
                    # Compute N(t) for all time intervals
                    import numpy
                    numpy.random.seed(12)
                    t = self.solver.t
                    dW = numpy.random.normal(loc=0, scale=1, size=len(t)-1)
                    dt = t[1:] - t[:-1]
                    self.N = self.sigma*dW/numpy.sqrt(dt)

                x, v = u
                N = self.N[self.solver.n]
                return [v, N -self.b*v -self.c*x]


We can easily compare different methods:


.. code-block:: python

        f = WhiteNoiseOscillator(b=0.1, c=pi**2, sigma=1)
        methods = [odespy.Heun(f), odespy.RK4(f),
                   odespy.ForwardEuler(f)]
        for method in methods:
            f.connect_solver(method)
            method.set_initial_condition([0,0])  # start from rest
            T = 60   # with c=pi**2, the period is 1
            u, t = method.solve(linspace(0, T, 10001))

            x = u[:,0]
            plot(t, x)
            hold(True)

        legend([str(m) for m in methods])



.. figure:: figs-tut/exsos1.png
   :width: 500

   *Oscillator driven by white noise*


The ``Heun`` and ``RK2`` methods give coinciding solutions while
the ``ForwardEuler`` method gives too large amplitudes.
The frequency is 0.5 (period 2) as expected.

In this example the white noise force is computed only once since
the ``f`` instance is reused in all methods. If a new ``f`` is created
for each method, it is crucial that the same seed of the random
generator is used for all methods, so that the time evolution of
the force is always the same - otherwise the solutions will be
different.





Inner Workings of the Package
=============================

The solvers are organized as classes in a class hierarchy with class
``Solver`` as superclass. Each class is initialized by the right-hand
side function (``f``) and an optional set of parameters for controlling
various parts of the solution process. Below we describe how the
superclass and its subclasses work and how parameters are registered
and initialized.

.. _odes:parameters:

Solver Parameters
-----------------

The ``ODE`` module defines a global dictionary ``_parameters`` holding
all legal parameters. Other modules imports this ``_parameters`` dict
and updates it with their own additional parameters.

For each parameter the ``_parameters`` dict stores the parameter name, a
default value, a description, the legal object type for the value of
the parameter, and other quantities if needed. A typical example
is

.. code-block:: py


        _parameters = dict(
        ...

        f = dict(
            help='Right-hand side f(u,t) defining the ODE',
            type=callable),

        f_kwargs = dict(
            help='Extra keyword arguments to f: f(u, t, *f_args, **f_kwargs)',
            type=dict,
            default={}),

        theta = dict(
            help="""Weight in [0,1] used for
        "theta-rule" finite difference approx.""",
            default=0.5,
            type=(int,float),
            range=[0, 1])

        ...
        }


Each solver class defines a (static) class variable
``_required_parameters`` for holding the names of all required
parameters (in a list). In addition, each solver class defines another
class variable ``_optional_parameters`` holding the names of all the
optional parameters. The doc strings of the solver classes are
automatically equipped with tables of required and optional
parameters.

The optional parameters of a class consists of the optional parameters
of the superclass and those specific to the class. The typical
initialization of ``_optional_parameters`` goes like this:

.. code-block:: python

        class SomeMethod(ParentMethod):
            _optional_parameters = ParentMethod._optional_parameters + \
                                   ['prm1', 'prm2', ...]

where ``prm1``, ``prm2``, etc. are names registered in the global
``_parameters`` dictionary.

From a user's point of view, the parameters are set either at
construction time or through the ``set`` function:

.. code-block:: py


        >>> from odespy import RK2
        >>> def f(u, t, a, b=0):
        ...   return a*u + b
        ...
        >>> method = RK2(f, f_kwargs=dict(b=1))
        >>> method.f_kwargs
        {'b': 1}
        >>> method.set(f_args=(3,))
        >>> method.f_args
        (3,)
        >>> # Get all registered parameters in the method instance
        >>> method.get()
        {'f_kwargs': {'b': 1}, 'f_args': (3,), 'complex_valued': False,
        'name of f': 'f'}

The ``set`` method sets parameters through keyword arguments and can
take an arbitrary collection of such arguments:

.. code-block:: python

        method.set(name1=value1, name2=value2, name3=value3, ...)


The ``get`` method returns the parameters and their values as a dictionary.
(Note that the ``'f'`` key, which one might expect to appear in the
returned dictionary of parameters, are omitted because it is always
a lambda function wrapping the user's ``f`` function such that the
returned value is guaranteed to be a ``numpy`` array. Instead,
there is an entry ``'name of f'`` which reflects the name of the
user-supplied function.)


Solver Classes
--------------

Each solver in this package is implemented as a class in a class hierarchy.
Basic, common functionality is inherited from super classes, and the
actual solver class implements what is specific for the method in question.

The Super Class
~~~~~~~~~~~~~~~

Class ``Solver`` is the super class of the hierarchy. Its constructor
requires one mandatory argument: the right-hand side of the ODE,
:math:`f(u,t)`, coded as a Python function ``f(u, t)`` or given as a string
containing code in a compiled language (Fortran, for instance)
implementing the right-hand side.  Additional keyword arguments can be
provided to set parameters of the solver.

The constructor performs a set of tasks that are common to all
the subclass solvers:

1. The set of optional and required parameters of a particular solver
   is loaded into ``self._parameters`` such that this dictionary
   can be used to look up all parameters of the solver.

2. Representation of :math:`f(u, t)` (or the Jacobian) in a compiled language
   is compiled into an extension module.

3. The solver-specific method ``adjust_parameters`` is called to allow
   the programmer of a solver to manipulate ``self._parameters``.
   For example, some existing or new parameters may be modified or set
   according to the value of other parameters.

4. All key-value pairs in ``self._parameters`` are mirrored by class
   attributes. The computations and the ``set`` and ``get`` methods will
   make use of the attributes rather than the ``self._parameters`` dict
   to extract data.  For example, the value of
   ``self._parameters['myvar']`` becomes available as ``self.myvar`` and
   in the algorithms we use ``self.myvar``, perhaps with a test
   ``hasattr(self, 'myvar')`` test or a `try`-`except` clause (catching
   an ``AttributeError``).

5. The ``set`` method is called with all keyword arguments to the
   constructor, which then modifies the default values of the
   parameters.

6. The ``f`` function is wrapped in a lambda function such that
   ``f(u, t)`` is guaranteed to return an array (in case the user
   returns a list or scalar for convenience).

7. The ``initialize`` method is called to finalize the tasks in
   the constructor. The most common use of this method in subclasses
   is to import extension modules that the solver depends on and
   provide an error message if the extension modules are not available.
   If they are, the modules are normally stored through an attribute
   of the subclass.

Let ``method`` some instance of a subclass in the hierarchy. The
following calls are possible (through inheriting common convenience
methods in the super class ``Solver``):

 * ``repr(method)``: return the subclass name along with all
   registered parameters and their values. This string provides
   complete information on the state of a subclass.

 * ``str(method)``: return a short pretty print string reflecting
   the name of the method and the value of parameters that
   must be known to uniquely define the numerical method.
   This string is what one would use as legends in a plot or
   as method identifier in a table.

 * ``method.get_parameter_info``: return or print all registered
   parameters for the current solver and all properties for
   each parameter.

After the constructor is called, ``method.set_initial_condition`` is
called to set the initial condition, and then ``solve`` is called.
The ``solve`` method features the following steps:

1. Convert ``time_points`` to a ``numpy`` array.

2. Call ``initialize_for_solve`` (implemented in subclasses) to
   precompute whatever is needed before the time loop.
   The super class allocates storage for the solution and
   loads the initial condition into that data structure.
   Any subclass implementation of ``initialize_for_solve`` must therefore
   also call this method in its super class.

3. Call ``validate_data`` to check if the data structures are consistent
   before starting the computations. Subclass implementations of
   this method must call the super class' version of the method.

4. Run a loop over all time levels ``n`` and call ``advance`` (implemented
   in subclasses) at each level to advance the solution from
   time ``t[n]`` to ``t[n+1]``. Also call ``terminate`` so that the
   user code can analyze and work with the solution.

Some subclasses will override the ``solve`` method and provide their own,
but most subclasses just inherits the general one and implement
the ``advance`` method.

All classes have a set of attributes:

1. ``users_f`` holding the user's function for :math:`f(u, t)`
   (implicit solvers will have a corresponding ``users_jac`` for
   the user's Jacobian),

2. one attribute for each parameter in the class,

3. ``u``: 1D ``numpy`` array holding the solution for a scalar ODE and
   a 2D array in case of a system of ODEs. The first index
   denotes the time level.

4. ``t``: the time levels corresponding to the first index in the ``u`` array.

5. ``quick_description``: a short one-line description of the method (this
   variable is static in the class, i.e., declared outside any method).

Most classes will also define two additional static variables,
``_required_parameters`` and ``_optional_parameters`` as explained
in the section :ref:`odes:parameters`.

A Very Simple Subclass
~~~~~~~~~~~~~~~~~~~~~~

To implement a simple explicit scheme for solving a scalar ODE or a system
of ODEs, you only need to write a subclass of ``Solver`` with an
``advance`` method containing the formula that updates the solution from
one time level to the next. For example, the Forward Euler scheme
reads

.. math::
         u_{n+1} = u_n + \Delta t f(u_n, t_n),

where subscript :math:`n` denotes the time level, and :math:`\Delta t = t_{n+1}-t_n` is
the current time step.
The implementation goes like

.. code-block:: python

        class ForwardEuler(Solver):
            """
            Forward Euler scheme::

                u[n+1] = u[n] + dt*f(u[n], t[n])
            """
            quick_description = 'The simple explicit (forward) Euler scheme'

            def advance(self):
                u, f, n, t = self.u, self.f, self.n, self.t
                dt = t[n+1] - t[n]
                unew = u[n] + dt*f(u[n], t[n])
                return unew

Remarks:

1. The ``quick_description`` is necessary for the class to appear in the
   automatically generated overview of implemented methods
   (run ``pydoc odespy`` to see this table).

2. Extracting class attributes in local variables (here ``u``, ``f``, etc.)
   avoids the need for the ``self`` prefix so that the implemented formulas
   are as close to the mathematical formulas as possible.

Almost equally simple schemes, like explicit Runge-Kutta methods and Heun's
method are implemented in the same way (see ``ODE.py``).

A 2nd-order Adams-Bashforth scheme is a bit more complicated since it
involves three time levels and therefore needs a separate method for
the first step. We should also avoid unnecessary evaluations of :math:`f(u,t)`.
The user can specify a parameter ``start_method`` for the name of the
solver to be used for the first step. This solver is initialized
by the ``switch_to`` method in class ``Solver``. Basically,

.. code-block:: python

        new_solver = solver.switch_to(solver_name)

creates a new solver instance ``new_solver``, of the class implied by
``solver_name``, where all relevant parameters from ``solver`` are coopied
to ``new_solver``.

An implementation of a subclass for the
2nd-order Adams-Bashforth scheme can then look as follows.

.. code-block:: python

        class AdamsBashforth2(Solver):
            """
            Second-order Adams-Bashforth method::

                u[n+1] = u[n] + dt/2.*(3*f(u[n], t[n]) - f(u[n-1], t[n-1]))

            for constant time step dt.

            RK2 is used as default solver in first step.
            """
            quick_description = "Explicit 2nd-order Adams-Bashforth method"

            _optional_parameters = Solver._optional_parameters + ['start_method',]

            def initialize_for_solve(self):
                # New solver instance for first step
                self.starter = self.switch_to(self.start_method)
                Solver.initialize_for_solve(self)

            def validate_data(self):
                if not self.constant_time_step():
                    print '%s must have constant time step' % self.__name__
                    return False
                else:
                    return True

            def advance(self):
                u, f, n, t = self.u, self.f, self.n, self.t

                if n >= 1:
                    dt = t[n+1] - t[n]  # must be constant
                    self.f_n = f(u[n], t[n])
                    unew = u[n] + dt/2.*(3*self.f_n - self.f_n_1)
                    self.f_n_1 = self.f_n
                else:
                    # User-specified method for the first step
                    self.starter.set_initial_condition(u[n])
                    time_points = [t[n], t[n+1]]
                    u_starter, t_starter = self.starter.solve(time_points)
                    unew = u_starter[-1]
                    self.f_n_1 = f(u[0], t[0])

                return unew

Three features are worth comments: 1) we extend the set of optional
parameters; 2) we must initialize a separate solver for the first
step, and this is done in the ``initialize_for_solve`` method that will
be called as part of ``solve`` (before the time stepping); and 3) we
extend ``validate_data`` to check that the time spacing given by the
``time_points`` argument to ``solve`` is constant. The utility method
``constant_time_step`` provided in super class ``Solver`` carries out the
details of the check.

More advanced implementations of subclasses can be studied
in the ``ODE.py`` and ``RungeKutta.py`` files.


Installation
============

The ``odespy`` package is most easily installed by checkout out
the latest version of the source code:

.. code-block:: console

        git clone git@github.com:hplgit/odespy.git
        cd odespy

The installation follows the expected standard procedure,

.. code-block:: console

        sudo python setup.py install


The ``odespy`` package depends on several other packages:

 * ``scipy`` for running the ``Vode`` Adams/BDF solver and the
   Dormand-Prince adaptive methods ``Dop853``, and ``Dopri5``.

 * ``sympy`` for running the extremely accurate ``SymPy_odefun`` solver.

These packages are readily downloaded and installed by the
standard ``setup.py`` script as shown above.
On Ubuntu and other Debian-based Linux systems the following
line installs all that ``odespy`` may need:

.. code-block:: console

        sudo apt-get install python-scipy python-nose python-sympy

'''

from solvers import *
from RungeKutta import *
from rkc import *
from rkf45 import *
from odepack import *

# Update doc strings with common info
class_, doc_str, classname = None, None, None
classnames = [name for name, obj in locals().items() \
               if inspect.isclass(obj)]

toc = []
for classname in classnames:
    class_ = eval(classname)
    doc_str = getattr(class_, '__doc__')
    setattr(class_, '__doc__',
            doc_str + table_of_parameters(class_))
    if hasattr(class_, 'quick_description'):
        toc.append((classname, getattr(class_, 'quick_description')))


# Make tables of solver name and quick description
__doc__ =  __doc__ + typeset_toc(toc) + __tutorial__

# Do not pollute namespace
del class_, doc_str, classname, classnames, toc, typeset_toc, \
    table_of_parameters, name, obj, inspect

if __name__ == '__main__':
    from os.path import join
    from numpy.testing import rundocs, run_module_suite
    import odespy
    path = odespy.__path__[0]

    # Doctests
    rundocs(join(path, 'ODE.py'))
    rundocs(join(path,'RungeKutta.py'))

    # Basic tests
    path = join(path, 'tests')
    run_module_suite(join(path, 'test_basics.py'))