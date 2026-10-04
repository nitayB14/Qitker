# Qitker API Reference

[Project overview](D0_Project_Overview.md) · [Installation](../../README.md#installation)

This reference introduces Qitker's circuit-building API in a progressive order. Section 1 covers the core objects, initialization, and register access. Section 2 covers single-qubit gates and rotations, including their matrices and API aliases. Section 3 covers register operations, circuit barriers, drawing, and structural inspection. Section 4 covers controlled gates, conditions, and ancilla-assisted register operations. Section 5 covers execution, measurement results, fidelity, leakage, and simulation limits. Section 6 covers Qiskit export, external simulation, and result decoding. Section 7 provides a method index and technical appendix.

## Contents

- [1. Foundations and core objects](#1-foundations-and-core-objects)
  - [1.1 Import and conventions](#11-import-and-conventions)
  - [1.2 Circuit — `circuit`](#12-circuit)
  - [1.3 Single qubit — `qubit`](#13-qubit)
  - [1.4 Qubit register — `qRegister`](#14-qregister)
  - [1.5 Register access and object information](#15-register-access-and-object-information)
  - [1.6 Bit order](#16-bit-order)
- [2. Single-qubit gates and rotations](#2-single-qubit-gates-and-rotations)
  - [2.1 Gate names and common behavior](#21-gate-names-and-common-behavior)
  - [2.2 Hadamard — H, `mix`, `superPosition`](#22-hadamard)
  - [2.3 Pauli X — bit flip, `flip`](#23-pauli-x)
  - [2.4 Pauli Y — `flipPhase`](#24-pauli-y)
  - [2.5 Pauli Z — phase flip, `phase`](#25-pauli-z)
  - [2.6 S gate — `halfPhase`](#26-s-gate)
  - [2.7 T gate — `quarterPhase`](#27-t-gate)
  - [2.8 Rotation about X — RX, `rotateX`](#28-rx)
  - [2.9 Rotation about Y — RY, `rotateY`](#29-ry)
  - [2.10 Rotation about Z — RZ, `rotateZ`](#210-rz)
  - [2.11 Phase relationships and execution support](#211-phase-relationships-and-execution-support)
- [3. Circuit and register operations](#3-circuit-and-register-operations)
  - [3.1 Elementwise gates on a register](#31-elementwise-gates-on-a-register)
  - [3.2 SWAP — `swap`](#32-swap)
  - [3.3 Cyclic register shifts — `shiftLeft`, `shiftRight`](#33-cyclic-shifts)
  - [3.4 Circuit barrier — `barrier`](#34-barrier)
  - [3.5 Drawing and text information](#35-drawing-and-text-information)
  - [3.6 Inspecting circuit structure](#36-inspecting-circuit-structure)
- [4. Controlled gates and conditions](#4-controlled-gates-and-conditions)
  - [4.1 Targets, controls, and method signatures](#41-signatures)
  - [4.2 One control: CX, CY, CZ, CS, and CT](#42-one-control)
  - [4.3 Multiple controls: CCX and general controlled gates](#43-multiple-controls)
  - [4.4 Static conditions with `where`](#44-where)
  - [4.5 Equality conditions with `==` and `where`](#45-equality)
  - [4.6 Controlled rotations](#46-controlled-rotations)
  - [4.7 A register as the target](#47-register-target)
  - [4.8 Compute, use, and uncompute with `ancilla`](#48-ancilla)
  - [4.9 Gate translation and execution support](#49-translation)
  - [4.10 Validation and common mistakes](#410-validation)
- [5. Execution, measurement, and results](#5-execution-measurement-and-results)
  - [5.1 Execute or measure a circuit](#51-execution)
  - [5.2 Counts, measured qubits, and shots](#52-counts)
  - [5.3 Select an outcome and read values](#53-selection)
  - [5.4 Measurement report API](#54-report)
  - [5.5 Output-state fidelity](#55-fidelity)
  - [5.6 Leakage probability](#56-leakage)
  - [5.7 State-space growth and practical limits](#57-limits)
  - [5.8 Measurement errors and result lifetime](#58-errors)
- [6. Qiskit export and execution paths](#6-qiskit-export-and-execution-paths)
  - [6.1 Export API and dependencies](#61-export)
  - [6.2 Translation of recorded operations](#62-mapping)
  - [6.3 Add the measurement mapping](#63-measurements)
  - [6.4 Complete Qiskit Aer example](#64-aer)
  - [6.5 Decode results and inspect the exported circuit](#65-decoding)
  - [6.6 Choose an execution path](#66-execution-paths)
  - [6.7 Export errors and common mistakes](#67-export-errors)
- [7. API index and technical appendix](#7-api-index-and-technical-appendix)
  - [7.1 Scope and constructors](#71-scope)
  - [7.2 Circuit method index](#72-circuit-index)
  - [7.3 Shared qubit and register methods](#73-shared-index)
  - [7.4 Controlled method signatures and aliases](#74-controlled-index)
  - [7.5 Object-specific methods and Python syntax](#75-object-index)
  - [7.6 Measurement report index](#76-report-index)
  - [7.7 Construction hooks and operation records](#77-internals)
  - [7.8 Troubleshooting and support lookup](#78-troubleshooting)

## 1. Foundations and core objects

### 1.1 Import and conventions

```python
from qitker import circuit, qubit, qRegister
```

The names are case-sensitive: `circuit` and `qubit` start with lowercase letters, while `qRegister` contains a capital `R`.

A `circuit` owns qubits and records their operations. A `qubit` represents one logical qubit in that circuit. A `qRegister` creates an ordered group of qubits in the same circuit.

Constructing these objects builds the circuit description; it does not run a simulation or sample a result. Gate methods append operations and normally return `None`. For a controlled operation such as `target.flipIf(control)`, the object receiving the method call is the **target**.

**Mathematical conventions.** States are column vectors. The single-qubit computational basis is ordered as $(|0\rangle, |1\rangle)$:

$$
|0\rangle = \begin{pmatrix}1\\0\end{pmatrix},
\qquad
|1\rangle = \begin{pmatrix}0\\1\end{pmatrix}.
$$

A gate matrix acts as $|\psi'\rangle = U|\psi\rangle$. For a displayed pair of qubits $(a,b)$, the basis order is $(|00\rangle, |01\rangle, |10\rangle, |11\rangle)$, with `a` on the left. Matrices for controlled gates must also identify which qubit is the control and which is the target. Rotation angles are in radians.

Matrices describe the intended logical operation. Execution through stored anyon braids may approximate that operation and may introduce leakage.

<a id="12-circuit"></a>

### 1.2 Circuit — `circuit`

**Constructor:** `circuit()` → a new `circuit` object.

```python
network = circuit()
```

The constructor takes no arguments. The new circuit has no qubits, no operations, and no measurement result. Create qubits or registers with `network` as their first argument; they register themselves automatically.

Qubits receive circuit-wide indices in creation order, starting at zero. Every control, target, and helper participating in an operation must belong to the same circuit. A circuit may contain several registers and individually created qubits.

Creating the circuit itself produces no quantum gate. The anyonic backend requires at least one qubit to execute a circuit, and measurement requires at least one qubit marked for measurement. The version 1 limit of two controls per gate is not a limit of three qubits per circuit.

<a id="13-qubit"></a>

### 1.3 Single qubit — `qubit`

**Constructor:** `qubit(quantumCircuit, initialize=0, measured=True)` → a new `qubit` object.

| Parameter | Accepted value | Meaning |
| --- | --- | --- |
| `quantumCircuit` | A `circuit` object | The circuit that owns the qubit. |
| `initialize` | Integer `0` or `1`; default `0` | The initial logical computational-basis value. Booleans are rejected. |
| `measured` | Boolean; default `True` | Whether to include this qubit in Qitker's measurement output and exported measurement mapping. |

```python
network = circuit()
first = qubit(network)                            # Index 0; initial |0>.
second = qubit(network, initialize=1)              # Index 1; prepare |1>.
helper = qubit(network, measured=False)            # Index 2; initial |0>.
```

**Translation to gates.** Logical qubits start in $|0\rangle$. `initialize=0` adds no preparation gate. `initialize=1` appends a Pauli-X gate:

$$
X = \begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad X|0\rangle = |1\rangle.
$$

`initialize` prepares a basis state; it does not accept an amplitude vector or reset an existing qubit. `measured=False` does not remove a qubit from the simulation or prevent gates from acting on it. It also does not automatically restore a helper qubit to zero.

An invalid circuit, a non-integer initializer, or a non-boolean `measured` raises `TypeError`. An integer initializer outside `{0, 1}` raises `ValueError`.

<a id="14-qregister"></a>

### 1.4 Qubit register — `qRegister`

**Constructor:** `qRegister(quantumCircuit, size=None, initialize=0, measured=True)` → a new `qRegister` object.

| Parameter | Accepted value | Meaning |
| --- | --- | --- |
| `quantumCircuit` | A `circuit` object | The circuit that owns every qubit in the register. |
| `size` | Positive integer or `None`; default `None` | Number of qubits. If omitted, inferred from `initialize`. Booleans are rejected. |
| `initialize` | Non-negative integer or non-empty binary string; default `0` | Initial value in Qitker's left-to-right register order. Booleans are rejected. |
| `measured` | Boolean; default `True` | Measurement flag applied to every newly created qubit. |

Each call allocates new qubits. It does not wrap or copy an existing collection of qubits.

**Size and padding rules:**

- An integer uses its minimum binary width when `size` is omitted; zero still uses one qubit.
- A string preserves its full width, including leading zeros.
- A larger explicit `size` pads the value with zeros on the left.
- A smaller explicit `size` is rejected, including when it would discard leading zeros from a string.
- Initialization strings contain only `0` and `1`. The wildcard `x` belongs to gate conditions, not initialization.

The following are independent construction examples; the bitstrings follow each register's own index order:

| Construction | Size | Initial bits, from register index 0 onward |
| --- | --- | --- |
| `qRegister(network)` | 1 | `0` |
| `qRegister(network, size=4)` | 4 | `0000` |
| `qRegister(network, initialize=5)` | 3 | `101` |
| `qRegister(network, size=4, initialize=5)` | 4 | `0101` |
| `qRegister(network, initialize="0001")` | 4 | `0001` |
| `qRegister(network, size=5, initialize="101")` | 5 | `00101` |

**Translation to gates.** The constructor allocates each qubit in order and adds X for every `1` in the padded initial bitstring. For `initialize="0101"`, X acts on register positions 1 and 3. This prepares a product basis state; the constructor introduces no entangling gates.

Invalid argument types raise `TypeError`. Negative integers, empty or non-binary strings, non-positive sizes, and initial values that do not fit the requested size raise `ValueError`.

### 1.5 Register access and object information

```python
network = circuit()
prefix = qubit(network)
register = qRegister(network, initialize="0101")

first = register[0]            # The first qubit; circuit index 1.
last = register[-1]            # The last qubit; circuit index 4.
same_first = register.getQubit(0)
pair = register[1:3]           # A list of two existing qubits.
all_qubits = register[:]       # A list of all four existing qubits.
reversed_qubits = register[::-1]

for current_qubit in register:
    print(current_qubit.getIndex())   # Prints 1, 2, 3, 4.
```

`register[index]` and `getQubit(index)` return the existing `qubit` object. They support ordinary Python list indexing, including negative indices; an out-of-range integer index raises `IndexError`.

A slice returns a Python `list`, not a `qRegister`. Its elements reference the original qubits, so applying a gate to an element affects the original circuit. Slicing, reversing a slice, and concatenating qubit lists add no gates and allocate no qubits. Reversing a list changes the reference order; it does not perform a quantum SWAP or register shift.

`qRegister` supports iteration through indexed access but does not define `len(register)`. Use `len(register[:])` to obtain its size.

| Method | On a `qubit` | On a `qRegister` |
| --- | --- | --- |
| `getIndex()` | Returns its circuit-wide integer index. | Returns a list of circuit-wide indices in register order. |
| `isToMeasure()` | Returns its boolean measurement flag. | Returns a list of flags, one per qubit. |
| `getQubit(index)` | Not available. | Returns the qubit at the requested position. |

For the example above, `register.getIndex()` returns `[1, 2, 3, 4]`, and `register.isToMeasure()` returns `[True, True, True, True]`. These methods inspect object metadata; they do not measure the quantum state.

`getValue()` and the register's `getBitstring()` read a **selected measurement outcome**, not the initializer or current amplitudes. They require a Qitker measurement followed by result selection; constructing an object alone does not make these values available.

### 1.6 Bit order

Qitker reads register strings from left to right. For a register initialized with `"0101"`:

| Register position | Initial bit | Binary place value |
| --- | --- | --- |
| `register[0]` | 0 | 8 |
| `register[1]` | 1 | 4 |
| `register[2]` | 0 | 2 |
| `register[3]` | 1 | 1 |

Thus index 0 is the leftmost, most-significant bit of the register's binary representation. A register position is distinct from a circuit-wide index: earlier allocations may shift the circuit-wide indices, as in the preceding example.

Qitker's measurement bitstrings follow circuit creation order, omitting qubits with `measured=False`. Register boundaries are not inserted into the bitstring.

Qiskit displays classical bitstrings in reverse classical-index order. When using Qitker's exported measurement mapping, reversing a plain result bitstring restores Qitker's measured-qubit order. The mapping and decoding must be reconsidered if the exported circuit's classical registers or measurements are changed.

## 2. Single-qubit gates and rotations

### 2.1 Gate names and common behavior

Every method in this section exists on both `qubit` and `qRegister`. On a qubit, a call appends one logical gate. On an $n$-qubit register, it appends the same gate to each qubit, implementing $U^{\otimes n}$ on that register. These elementwise operations do not entangle an initially unentangled register.

All methods return `None`. Aliases in one row below are alternative names for the same operation; calling several aliases in succession applies the gate several times.

| Professional name | Qitker methods (on a qubit or register) | Logical operation | Qiskit export per target |
| --- | --- | --- | --- |
| Hadamard | `H()`, `h()`, `superPosition()`, `mix()` | H | `qc.h(index)` |
| Pauli X / bit-flip gate | `X()`, `x()`, `flip()` | X | `qc.x(index)` |
| Pauli Y | `Y()`, `y()`, `flipPhase()` | Y | `qc.y(index)` |
| Pauli Z / phase-flip gate | `Z()`, `z()`, `phase()` | Z | `qc.z(index)` |
| S / phase gate | `S()`, `s()`, `halfPhase()` | S | `qc.s(index)` |
| T / pi-over-eight gate | `T()`, `t()`, `quarterPhase()` | T | `qc.t(index)` |
| X-axis rotation | `rotateX(angle)`, `RX(angle)` | RX | `qc.rx(angle, index)` |
| Y-axis rotation | `rotateY(angle)`, `RY(angle)` | RY | `qc.ry(angle, index)` |
| Z-axis rotation | `rotateZ(angle)`, `RZ(angle)` | RZ | `qc.rz(angle, index)` |

Here, `index` is the target's circuit-wide index. These names are case-sensitive: for example, `superPosition` has a capital `P`, and the rotation aliases are `RX`, `RY`, and `RZ`; lowercase `rx`, `ry`, and `rz` are not Qitker methods.

All matrices below use the ordered basis $(|0\rangle, |1\rangle)$, with $i^2=-1$. Each short example assumes this setup and is independent of the other examples:

```python
import math
from qitker import circuit, qubit, qRegister

network = circuit()
q = qubit(network)
```

<a id="22-hadamard"></a>

### 2.2 Hadamard gate — `H()`, `h()`, `superPosition()`, `mix()`

The Hadamard gate converts computational-basis states into equal superpositions with different relative signs:

$$
H = \frac{1}{\sqrt{2}}\begin{pmatrix}1&1\\1&-1\end{pmatrix},
\qquad
H|0\rangle = \frac{|0\rangle+|1\rangle}{\sqrt{2}} = |+\rangle,
\qquad
H|1\rangle = \frac{|0\rangle-|1\rangle}{\sqrt{2}} = |-\rangle.
$$

```python
q.mix()  # Appends H; prepares |+> from the initial |0>.
```

This is a coherent unitary transformation, not a random choice of zero or one. It does not produce an equal superposition for every possible input: for example, $H|+\rangle=|0\rangle$. Applying it twice gives $H^2=I$.

<a id="23-pauli-x"></a>

### 2.3 Pauli-X gate — `X()`, `x()`, `flip()`

X swaps the two computational-basis amplitudes:

$$
X = \begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad X|0\rangle=|1\rangle,
\qquad X|1\rangle=|0\rangle.
$$

```python
q.flip()  # Appends X; prepares |1> from the initial |0>.
```

For a general input $\alpha|0\rangle+\beta|1\rangle$, the result is $\beta|0\rangle+\alpha|1\rangle$. Applying X twice gives $X^2=I$.

<a id="24-pauli-y"></a>

### 2.4 Pauli-Y gate — `Y()`, `y()`, `flipPhase()`

Y exchanges the basis states and introduces complex phases:

$$
Y = \begin{pmatrix}0&-i\\i&0\end{pmatrix},
\qquad Y|0\rangle=i|1\rangle,
\qquad Y|1\rangle=-i|0\rangle.
$$

```python
q.flipPhase()  # Appends one Y gate; maps the initial |0> to i|1>.
```

The exact matrix identity is $Y=iXZ$. `flipPhase()` records a Y gate directly; it does not append separate X and Z gates. A manually written sequence of X and Z can differ from Y by a global phase. Applying Y twice gives $Y^2=I$.

<a id="25-pauli-z"></a>

### 2.5 Pauli-Z gate — `Z()`, `z()`, `phase()`

Z leaves the zero component unchanged and reverses the sign of the one component, adding a relative phase of $\pi$:

$$
Z = \begin{pmatrix}1&0\\0&-1\end{pmatrix},
\qquad Z|0\rangle=|0\rangle,
\qquad Z|1\rangle=-|1\rangle.
$$

```python
q.mix()
q.phase()  # Appends Z after H; changes |+> into |->.
```

Z does not change computational-basis probabilities immediately, but its relative phase affects later interference. `phase()` takes no angle argument and always means Z. Applying Z twice gives $Z^2=I$.

<a id="26-s-gate"></a>

### 2.6 S gate — `S()`, `s()`, `halfPhase()`

S adds a relative phase of $\pi/2$ to the one component. It is a square root of Z:

$$
S = \begin{pmatrix}1&0\\0&i\end{pmatrix},
\qquad S|0\rangle=|0\rangle,
\qquad S|1\rangle=i|1\rangle,
\qquad S^2=Z.
$$

```python
q.mix()
q.halfPhase()  # Prepares (|0> + i|1>)/sqrt(2) in the ideal circuit.
```

The name `halfPhase` refers to half the relative phase of Z. The method appends one S gate and takes no parameters.

<a id="27-t-gate"></a>

### 2.7 T gate — `T()`, `t()`, `quarterPhase()`

T adds a relative phase of $\pi/4$ to the one component. It is commonly called the **pi-over-eight gate** ($\pi/8$ gate), although the relative phase in the standard matrix is $\pi/4$:

$$
T = \begin{pmatrix}1&0\\0&e^{i\pi/4}\end{pmatrix},
\qquad T|0\rangle=|0\rangle,
\qquad T|1\rangle=e^{i\pi/4}|1\rangle.
$$

```python
q.mix()
q.quarterPhase()  # Prepares (|0> + exp(i*pi/4)|1>)/sqrt(2).
```

The name `quarterPhase` refers to one quarter of Z's relative phase. The method appends one T gate and takes no parameters. Exactly, $T^2=S$ and $T^4=Z$. Its relationship to a Z rotation is $T=e^{i\pi/8}R_Z(\pi/4)$, which explains the pi-over-eight terminology.

<a id="28-rx"></a>

### 2.8 X-axis rotation — `rotateX(angle)`, `RX(angle)`

For a real angle $\theta$ in radians, RX rotates the Bloch vector about the X axis. Qitker requires the `angle` argument and passes it to the exported rotation gate unchanged:

$$
R_X(\theta)=e^{-i\theta X/2}
=\begin{pmatrix}
\cos(\theta/2)&-i\sin(\theta/2)\\
-i\sin(\theta/2)&\cos(\theta/2)
\end{pmatrix}.
$$

```python
q.rotateX(angle=math.pi / 2)  # Ideal result: (|0> - i|1>)/sqrt(2).
```

The call appends an RX operation with the supplied angle. At $\theta=\pi$, $R_X(\pi)=-iX$; it is not exactly the X matrix.

<a id="29-ry"></a>

### 2.9 Y-axis rotation — `rotateY(angle)`, `RY(angle)`

RY rotates the Bloch vector about the Y axis. Its required `angle` argument is in radians:

$$
R_Y(\theta)=e^{-i\theta Y/2}
=\begin{pmatrix}
\cos(\theta/2)&-\sin(\theta/2)\\
\sin(\theta/2)&\cos(\theta/2)
\end{pmatrix}.
$$

```python
q.rotateY(math.pi / 2)  # Ideal result: |+> from the initial |0>.
```

The call appends an RY operation. Although $R_Y(\pi/2)$ and H both map $|0\rangle$ to $|+\rangle$, they are different operators: their actions on $|1\rangle$ differ. At $\theta=\pi$, $R_Y(\pi)=-iY$.

<a id="210-rz"></a>

### 2.10 Z-axis rotation — `rotateZ(angle)`, `RZ(angle)`

RZ rotates the Bloch vector about the Z axis. Its required `angle` argument is in radians:

$$
R_Z(\theta)=e^{-i\theta Z/2}
=\begin{pmatrix}
e^{-i\theta/2}&0\\
0&e^{i\theta/2}
\end{pmatrix}.
$$

```python
q.mix()
q.rotateZ(math.pi / 2)
# Ideal result: (exp(-i*pi/4)|0> + exp(i*pi/4)|1>)/sqrt(2).
```

The call appends an RZ operation. The relative phase between the one and zero components changes by $\theta$, while both components receive phase factors. Therefore $R_Z(\theta)$ differs by a global phase from $\operatorname{diag}(1,e^{i\theta})$.

### 2.11 Phase relationships and execution support

For any axis $A\in\{X,Y,Z\}$, $R_A(0)=I$, $R_A(-\theta)=R_A(\theta)^\dagger$, and $R_A(2\pi)=-I$. Negative angles implement inverse rotations. Angles are passed through as supplied; Qitker does not replace a zero-angle call with an omitted gate or convert special angles into fixed gates.

The exact relationships for fixed phase gates are:

$$
Z=e^{i\pi/2}R_Z(\pi),\qquad
S=e^{i\pi/4}R_Z(\pi/2),\qquad
T=e^{i\pi/8}R_Z(\pi/4).
$$

A global phase multiplying the entire state does not change measurement probabilities. However, turning two gates that differ by a global phase into controlled gates makes that phase relative between control branches. Their controlled versions cannot generally be substituted for one another without a correction.

The frontend records the gate selected by the method name. For example, `halfPhase()` records S, whereas `rotateZ(math.pi / 2)` records RZ with an angle; it does not become an S operation.

| Gate family | Circuit construction and Qiskit export | Version 1 anyonic execution |
| --- | --- | --- |
| H, X, Y, Z, S, T and their aliases | Supported; mapped as listed in section 2.1. | Supported through stored braid sequences, with approximation and possible leakage. |
| RX, RY, RZ and their aliases | Supported with the supplied angle. | Unsupported: parameterized rotations are not implemented by the current anyonic execution path. |

Use Qiskit export to simulate the rotation examples above. Even a special angle such as `rotateX(math.pi)` remains a rotation operation and is not automatically routed to the stored X braid sequence.

For a register, the same names and angles apply independently to every element:

```python
network = circuit()
register = qRegister(network, size=3)
register.quarterPhase()       # Three T operations: T tensor T tensor T.
register.rotateY(math.pi / 4) # Three RY(pi/4) operations; use Qiskit export.
```

None of the methods in this section accepts `control`, `where`, or `ancilla`. Conditional variants have separate method names. There are no dedicated `sdg()` or `tdg()` methods in the current API; logically, $S^\dagger=S^3$ and $T^\dagger=T^7$ can be expressed by repeated calls to the existing gates.

## 3. Circuit and register operations

### 3.1 Elementwise gates on a register

The [single-qubit methods in section 2](#21-gate-names-and-common-behavior) also operate on a whole `qRegister`. A call applies the chosen gate once to every qubit in register order and returns `None`.

```python
from qitker import circuit, qubit, qRegister

network = circuit()
register = qRegister(network, size=2)
register.mix()  # Equivalent to register[0].mix(); register[1].mix().
```

For a gate $U$ on an $n$-qubit register, the register operation is the tensor product $U^{\otimes n}$. For example, `mix()` on two qubits implements the following matrix in the ordered basis $(|00\rangle,|01\rangle,|10\rangle,|11\rangle)$:

$$
H\otimes H=\frac{1}{2}
\begin{pmatrix}
1&1&1&1\\
1&-1&1&-1\\
1&1&-1&-1\\
1&-1&-1&1
\end{pmatrix}.
$$

This prepares $(|00\rangle+|01\rangle+|10\rangle+|11\rangle)/2$ from $|00\rangle$. It is a product state, not a Bell state. Two H operations are recorded and exported; Qitker does not construct a new two-qubit gate for the tensor product.

To act on selected positions, iterate over a slice:

```python
for current_qubit in register[:1]:
    current_qubit.flip()  # Acts only on register[0].
```

A slice is a Python list, so `register[:1].flip()` is not valid. For an $n$-qubit register, a fixed gate or rotation call appends $n$ operations. Its execution support is the same as that of the underlying gate; register operations do not make parameterized rotations available in the anyonic backend.

<a id="32-swap"></a>

### 3.2 SWAP gate — `qubit.swap(control)`

**Signature:** `a.swap(control)` → `None`, where `control` is the other `qubit` to exchange with `a`.

Despite the parameter name `control`, this is an unconditional SWAP. The two operands must be distinct qubits belonging to the same circuit. SWAP exchanges their quantum states, including correlations with other qubits; their Python objects, indices, and measurement flags remain unchanged.

In the ordered basis $(|a b\rangle)=(|00\rangle,|01\rangle,|10\rangle,|11\rangle)$:

$$
\operatorname{SWAP}=
\begin{pmatrix}
1&0&0&0\\
0&0&1&0\\
0&1&0&0\\
0&0&0&1
\end{pmatrix},
\qquad
\operatorname{SWAP}|a b\rangle=|b a\rangle.
$$

```python
network = circuit()
a = qubit(network, initialize=1)
b = qubit(network)
a.swap(b)  # Ideal state changes from |10> to |01> in (a, b) order.
```

**Translation to gates.** `a.swap(b)` appends these three controlled-X gates, in execution order:

```python
a.flipIf(b)  # b controls X on a.
b.flipIf(a)  # a controls X on b.
a.flipIf(b)  # b controls X on a.
```

This block explains the decomposition; do not append it after `a.swap(b)` unless a second SWAP is intended. The exporter emits three `qc.cx(...)` calls, not `qc.swap(...)`. The anyonic backend executes the corresponding CX braid sequences. SWAP itself adds three logical gates, excluding any earlier initialization gates.

A non-qubit operand raises `TypeError`. Swapping a qubit with itself or with a qubit from another circuit raises `ValueError`. There is no whole-register `swap()` method; exchange chosen qubits individually.

<a id="33-cyclic-shifts"></a>

### 3.3 Cyclic register shifts — `shiftLeft(amount=1)`, `shiftRight(amount=1)`

These `qRegister` methods rotate the register's quantum contents cyclically and return `None`. Supply an integer `amount`; positive values move in the named direction, and negative values reverse it. The amount is reduced modulo the register size. A zero shift, a whole-register-length shift, or any shift on a one-qubit register adds no gates.

For three qubits in register order, the left-shift permutation $L$ and right-shift permutation $R$ act as:

$$
L|b_0b_1b_2\rangle=|b_1b_2b_0\rangle,\qquad
R|b_0b_1b_2\rangle=|b_2b_0b_1\rangle.
$$

For an $n$-qubit register and normalized left-shift amount $k$, the complete matrix can be written without listing all $2^n\times2^n$ entries:

$$
L_k=\sum_{b_0,\ldots,b_{n-1}\in\{0,1\}}
|b_k\cdots b_{n-1}b_0\cdots b_{k-1}\rangle
\langle b_0\cdots b_{n-1}|,
\qquad R_k=L_k^\dagger=L_{(-k)\bmod n}.
$$

For $k=0$, this is the identity. Each column of $L_k$ has a single 1 at the row for the shifted bitstring, with all other entries zero. The same permutation acts linearly on superpositions; no bits are discarded or replaced with zeros.

Starting independently from `"1001"`, the ideal results are:

| Call | Result in Qitker register order |
| --- | --- |
| `register.shiftLeft()` | `0011` |
| `register.shiftRight()` | `1100` |
| `register.shiftLeft(2)` | `0110` |
| `register.shiftLeft(4)` | `1001` |
| `register.shiftRight(5)` | `1100` |
| `register.shiftLeft(-1)` | `1100` |

```python
network = circuit()
register = qRegister(network, initialize="1001")
register.shiftLeft(1)   # Ideal contents: 0011.
register.shiftRight(1)  # Restores the ideal contents: 1001.
```

**Translation to gates.** Qitker constructs the required permutation using qubit SWAPs, each expanded into three CX gates. For a four-qubit left shift by one, it swaps positions `(0, 1)`, then `(1, 2)`, then `(2, 3)`: nine CX gates in total. Other amounts can use different SWAP sequences. Qiskit export preserves the generated CX operations; the anyonic backend executes their stored braid sequences.

The register retains the same qubit objects at the same Python positions. Thus `register[0]` still refers to the original object, but its quantum contents have changed. In contrast, `register[::-1]` only returns references in reverse order and adds no quantum operation.

<a id="34-barrier"></a>

### 3.4 Circuit barrier — `circuit.barrier()`

**Signature:** `network.barrier()` → `None`.

A barrier marks a boundary across the circuit's qubits. It takes no arguments; there is no subset-of-qubits parameter.

```python
network = circuit()
register = qRegister(network, size=2)
register.mix()
network.barrier()
register.flip()
```

A barrier is a circuit directive, not a quantum gate with its own unitary matrix. It leaves the state unchanged. Qitker stores it as an operation named `"barrier"`, displays it with `@` markers, and exports it as `qc.barrier()`.

The anyonic executor skips barriers. They add no braids and are excluded from the measurement report's logical gate count, although they remain present in `getOperationVector()`. Adding a barrier still invalidates a previously selected measurement result, just as adding another operation does.

### 3.5 Drawing and text information

| Call | Behavior | Return value |
| --- | --- | --- |
| `network.draw()` | Prints a text circuit diagram. | `None` |
| `network.details()` | Prints a circuit heading, qubit count, and diagram. | `None` |
| `str(network)` | Produces a qubit count and per-qubit metadata. | `str` |
| `str(q)` | Produces the qubit's circuit index and measurement flag. | `str` |

```python
network = circuit()
data = qubit(network)
helper = qubit(network, measured=False)
data.mix()
helper.flipIf(data)
network.barrier()
network.draw()
```

In the drawing, `q[index]` identifies a qubit included in measurement, while `A[index]` identifies one with `measured=False`. The `A` label does not establish any special ancilla state. Controlled operations show a dot at each control and the underlying gate name at the target. The diagram displays the recorded decomposition: a SWAP appears as three controlled-X operations.

Call `draw()` directly rather than `print(network.draw())`, which also prints the returned `None`. The current `details()` implementation itself uses that pattern and prints an extra `None` after its diagram. The drawing shows rotation names but not their angle values; inspect the operation records to obtain those angles.

`str(register)` concatenates its qubits' metadata; the current implementation also prints that metadata while creating the string. `repr()` uses the corresponding string implementation for all three object types. These displays describe circuit structure, not amplitudes or measurement results. Drawing and metadata inspection do not add gates or execute a simulation.

### 3.6 Inspecting circuit structure

All indices returned here are circuit-wide indices, not positions within a particular register.

| Method | Return value and meaning |
| --- | --- |
| `getQubitsNumber()` | Integer count of all qubits, including unmeasured helpers. |
| `getQubitsNumberToMeasure()` | Integer count of qubits whose measurement flag is `True`. |
| `getQubitsArray()` | The circuit's list of qubit objects, in creation order. |
| `getIndex(qubit)` | The position of the given qubit in that list; an absent qubit raises `ValueError`. |
| `getOperationVector()` | A NumPy array containing recorded operation objects in execution order. |

`getQubitsArray()` and `getOperationVector()` expose internal containers, not defensive copies. Use them for inspection; direct edits bypass the normal bookkeeping for circuit construction and measurement results.

An operation record exposes getters according to its type:

| Getter | Available on | Meaning |
| --- | --- | --- |
| `getName()` | Every operation, including barriers. | Logical name such as `"H"`, `"X"`, `"RX"`, or `"barrier"`. |
| `getTarget()` | Gate operations. | Target qubit index. |
| `getControllers()` | Controlled gate operations. | List of control qubit indices. |
| `getAngle()` | Rotation operations, including controlled rotations. | The angle supplied to the gate. |

A controlled-X record has name `"X"` and a controller list; its name is not `"CX"`. A barrier has neither a target nor controllers nor an angle. This inspection pattern handles all these cases:

```python
for recorded in network.getOperationVector():
    info = {"name": recorded.getName()}
    if hasattr(recorded, "getTarget"):
        info["target"] = recorded.getTarget()
    if hasattr(recorded, "getControllers"):
        info["controls"] = recorded.getControllers()
    if hasattr(recorded, "getAngle"):
        info["angle"] = recorded.getAngle()
    print(info)
```

The vector includes initialization X gates, expanded operations such as the three CX gates of SWAP, and barriers. Its length is therefore not the number of high-level method calls, and it differs from the report's gate count when barriers are present. These metadata methods have no quantum matrix: they read the description of the circuit without transforming its state.

## 4. Controlled gates and conditions

A controlled operation applies a gate only in the computational-basis branches that satisfy a condition. It is a coherent quantum operation: Qitker does not measure the controls or make a classical decision before adding the gate. A superposition of matching and nonmatching inputs can become entangled with the target.

<a id="41-signatures"></a>

### 4.1 Targets, controls, and method signatures

The object receiving the call is the **target**; `control` specifies the condition inputs. All methods in this chapter append operations and return `None`.

| Method | Gate on a matching branch | Aliases on `qubit` only |
| --- | --- | --- |
| `flipIf` | X | `cx(control)`, `CX(control)` |
| `flipPhaseIf` | Y | `cy(control)`, `CY(control)` |
| `phaseIf` | Z | `cz(control)`, `CZ(control)` |
| `halfPhaseIf` | S | `cs(control)`, `CS(control)` |
| `quarterPhaseIf` | T | `ct(control)`, `CT(control)` |

For each of the five methods, the signatures are:

```text
qubit.method(control, where=None)
qRegister.method(control, where=None, ancilla=None)
```

Here, `method` stands for a name in the table, not a literal API method. The uppercase/lowercase aliases accept only `control`; use the `...If` names to supply `where`. A register target exposes the five `...If` methods, but not the `cx`/`CX`-style aliases. Controlled rotations have the separate signatures in [section 4.6](#46-controlled-rotations).

| Argument | Accepted forms | Meaning |
| --- | --- | --- |
| `control` | A `qubit`, a non-empty Python list of qubits, a `qRegister`, or a supported equality expression | The controls in the order used by the condition. |
| `where` | `None`, an integer, a pattern string, or quantum comparison operands | Which control values activate the gate. |
| `ancilla` | `None` or a `qubit`; register targets only | Optional workspace for computing the condition once. |

A register control is expanded into its qubit list. Tuples are not accepted as control lists. With `where=None`, all controls must be `1`; a list means an AND of the controls, not an OR or a sequence of independent gates.

```python
from qitker import circuit, qubit, qRegister

network = circuit()
control = qubit(network)
target = qubit(network)
control.mix()
target.flipIf(control)  # CX: control is the control, target is the target.
```

This prepares a Bell state in the ideal logical circuit. Even when the control was initialized to zero, the call still records a controlled operation; Qitker does not remove it based on that initializer.

<a id="42-one-control"></a>

### 4.2 One control: CX, CY, CZ, CS, and CT

For a control `c` and target `t`, all matrices here use the explicit order
$(|c t\rangle)=(|00\rangle,|01\rangle,|10\rangle,|11\rangle)$.
For a single-qubit gate $U$:

$$
C(U)=|0\rangle\langle0|\otimes I_2
+|1\rangle\langle1|\otimes U
=\begin{pmatrix}I_2&0\\0&U\end{pmatrix}.
$$

Thus the first two basis states are unchanged; the last two receive U. The underlying matrices are defined in [section 2](#2-single-qubit-gates-and-rotations).

**CX / CNOT — `target.flipIf(control)`:**

$$
CX=\begin{pmatrix}
1&0&0&0\\0&1&0&0\\0&0&0&1\\0&0&1&0
\end{pmatrix}.
$$

It exchanges $|10\rangle$ and $|11\rangle$: the target flips exactly when the control is one.

**CY — `target.flipPhaseIf(control)`:**

$$
CY=\begin{pmatrix}
1&0&0&0\\0&1&0&0\\0&0&0&-i\\0&0&i&0
\end{pmatrix}.
$$

It sends $|10\rangle$ to $i|11\rangle$ and $|11\rangle$ to $-i|10\rangle$. The phases are part of CY; a classical truth table alone does not describe this gate.

**CZ, CS, and CT — controlled phase gates:**

$$
CZ=\operatorname{diag}(1,1,1,-1),\qquad
CS=\operatorname{diag}(1,1,1,i),\qquad
CT=\operatorname{diag}(1,1,1,e^{i\pi/4}).
$$

These correspond to `phaseIf`, `halfPhaseIf`, and `quarterPhaseIf`. They add a phase of $\pi$, $\pi/2$, or $\pi/4$ only to $|11\rangle$. If the target is zero, applying Z, S, or T leaves that branch unchanged even when the control matches.

Qitker records one controlled operation in each case. These matrices use control-first notation for readability; raw Qiskit matrices use Qiskit's subsystem ordering and must be reordered before entry-by-entry comparison.

<a id="43-multiple-controls"></a>

### 4.3 Multiple controls: CCX and general controlled gates

Pass several controls to the same method:

```python
network = circuit()
controls = qRegister(network, size=2)
target = qubit(network)
target.flipIf(controls)  # CCX / Toffoli: both controls must be 1.
```

Using `controls[:]` instead of `controls` is equivalent. On a qubit target, `target.cx(controls)` is also valid: the alias does not restrict the number of controls. There are no separate `ccx()` or `CCX()` methods.

For $n$ controls followed by one target in the basis order, let $P_n=|1\cdots1\rangle\langle1\cdots1|$. Then:

$$
C^n(U)=(I_{2^n}-P_n)\otimes I_2+P_n\otimes U
=\operatorname{diag}(I_{2^{n+1}-2},U).
$$

For two controls, the basis is $(|000\rangle,|001\rangle,\ldots,|111\rangle)$, with the target last. In particular:

$$
CCX=\operatorname{diag}(I_6,X),\qquad
CCY=\operatorname{diag}(I_6,Y),\qquad
CCZ=\operatorname{diag}(1,1,1,1,1,1,1,-1).
$$

CCX swaps only $|110\rangle$ and $|111\rangle$. CCS and CCT similarly multiply only $|111\rangle$ by $i$ and $e^{i\pi/4}$, respectively. The same construction defines gates with more controls, but their anyonic execution support is limited as described in [section 4.9](#49-translation).

<a id="44-where"></a>

### 4.4 Static conditions with `where`

For `control=[a, b, c]`, the first pattern character refers to `a`, the second to `b`, and the third to `c`. This is the supplied list order, even if it differs from circuit-index order.

| Condition | Matching inputs for three controls |
| --- | --- |
| `where=None` | `111` |
| `where="010"` | `010` |
| `where=2` | `010`, after padding the integer to three bits |
| `where="1x0"` | `100` and `110`; the middle control is ignored |
| `where="xxx"` | Every input; the target operation becomes unconditional |

Strings must have exactly one character per supplied control and contain only `0`, `1`, or `x`; uppercase `X` is also accepted. Integers must satisfy $0\leq\texttt{where}<2^n$, where $n$ is the number of supplied controls. Booleans are rejected. For several controls, integer `where=1` means the padded pattern `00...01`, not all ones.

For a pattern $p$, define the projector onto its matching control states:

$$
\Pi_p=\bigotimes_{j=0}^{n-1}Q_{p_j},\qquad
Q_0=|0\rangle\langle0|,\quad
Q_1=|1\rangle\langle1|,\quad Q_x=I_2.
$$

The complete conditional matrix, with controls before the target, is:

$$
V_{p,U}=(I_{2^n}-\Pi_p)\otimes I_2+\Pi_p\otimes U.
$$

For a single control on zero, this becomes $\operatorname{diag}(U,I_2)$, often called a negative or open control. For an all-`x` pattern it becomes $I_{2^n}\otimes U$.

**Translation to gates:**

1. Append X to every control marked `0`.
2. Append the gate controlled on all non-`x` positions being `1`. If none remain, append the unconditional gate.
3. Undo the X gates in reverse order.

For example, this construction:

```python
network = circuit()
controls = qRegister(network, size=3)
target = qubit(network)
target.flipIf(controls, where="1x0")
```

records the same sequence as this alternative block:

```python
controls[2].flip()
target.flipIf([controls[0], controls[2]])
controls[2].flip()
```

It contains two X gates and one CCX; the ignored control adds no gate. Use either construction, not both. On a superposition, this remains a coherent operation on all matching branches. Ignoring a control does not bypass validation: even an `x` position must contain a valid, distinct control from the same circuit, separate from the target.

<a id="45-equality"></a>

### 4.5 Equality conditions with `==` and `where`

Qitker overloads `==` to describe selected conditions. Creating the expression alone adds no gates; passing it to a controlled method builds the operation.

| Expression passed as `control` | Equivalent call using `where` |
| --- | --- |
| `target.flipIf(a == b)` for two qubits | `target.flipIf(a, where=b)` |
| `target.flipIf(left == right)` for registers | `target.flipIf(left, where=right)` |
| `target.flipIf(register == "1x0")` | `target.flipIf(register, where="1x0")` |
| `target.flipIf(register == 2)` | `target.flipIf(register, where=2)` |

The same condition forms work with the other fixed controlled gates, controlled rotations, and register targets. Register comparisons to strings or integers use the static-pattern translation above; a wildcard string denotes a pattern match rather than exact numerical equality.

**Quantum equality.** For two disjoint $n$-qubit operands $L$ and $R$, equality means matching computational-basis bitstrings in each branch, not comparing two unknown statevectors or their amplitudes. Define:

$$
\Pi_{\mathrm{eq}}=\sum_{x=0}^{2^n-1}
|x\rangle\langle x|_L\otimes|x\rangle\langle x|_R.
$$

In the order $(L,R,\text{target})$, the operation is:

$$
V_{\mathrm{eq},U}=(I_{2^{2n}}-\Pi_{\mathrm{eq}})\otimes I_2
+\Pi_{\mathrm{eq}}\otimes U.
$$

For two single-qubit operands and an X target, this is the explicit block matrix $\operatorname{diag}(X,I_2,I_2,X)$: the equal inputs `00` and `11` activate X.

**Translation to gates:** compute each bitwise XOR into the right-hand operand using CX, apply U conditioned on that entire operand being zero, then reverse the XOR computation. No extra qubits are allocated for this comparison.

```python
network = circuit()
left = qRegister(network, size=2)
right = qRegister(network, size=2)
target = qubit(network)
target.flipIf(left == right)
```

The call expands to the following alternative sequence:

```python
right[0].flipIf(left[0])
right[1].flipIf(left[1])
target.flipIf(right, where=0)
right[1].flipIf(left[1])
right[0].flipIf(left[0])
```

The middle call further expands to X on both right-hand qubits, CCX on the target, then X on both right-hand qubits again. For width $n$, the construction contains $2n$ CX gates, $2n$ X gates, and one $C^n(U)$ operation. Uncomputation removes the temporary XOR encoding; the intended controlled operation can still entangle the operands with the target.

**Forms and restrictions:**

- Quantum operands must be equally sized and either disjoint or exactly the same qubits in the same order. Partial overlap and reordered overlap are rejected.
- Comparing an operand with itself simplifies to an unconditional target gate after validation. It does not inspect the quantum state.
- `qubit == qubit` is supported. For a qubit compared to a constant, use `where=0` or `where=1`; `qubit == 0` does not create the supported symbolic condition.
- `left[:] == right[:]` uses Python list equality. For lists or slices, use `target.flipIf(left[:], where=right[:])` instead. Both sides must normalize to lists; a bare qubit must be compared with a bare qubit.
- Do not supply an explicit `where` alongside an equality expression; this raises `TypeError`.

These expressions are not classical measurement tests. In particular, `if left == right:` does not check quantum values: the current condition object's boolean conversion checks Python operand identity. Do not combine these conditions with Python `and`, `or`, or `not`, chained comparisons, or bitwise `&`/`|`. There is no dedicated API for general logical combinations, `!=`, or ordering comparisons. More complex predicates can be constructed explicitly with flag qubits and reversible gates, as in [EX3](D3_advanced_grover.md).

<a id="46-controlled-rotations"></a>

### 4.6 Controlled rotations

| Target type | Signatures |
| --- | --- |
| `qubit` | `rotateXif(control, angle=0, where=None)`, `rotateYif(control, angle=0, where=None)`, `rotateZif(control, angle=0, where=None)` |
| `qRegister` | `rotateXif(control, angle, where=None, ancilla=None)`, `rotateYif(control, angle, where=None, ancilla=None)`, `rotateZif(control, angle, where=None, ancilla=None)` |

`if` is lowercase in these names. All return `None`. The angle is in radians and is required for a register target. Although a qubit target defaults to zero, passing the angle explicitly makes the intended operation clear. There are no separate `crx`/`CRX`, `cry`/`CRY`, or `crz`/`CRZ` aliases.

For one positive control and the control-first basis of section 4.2, put $c=\cos(\theta/2)$ and $s=\sin(\theta/2)$:

$$
CR_X(\theta)=\begin{pmatrix}
1&0&0&0\\0&1&0&0\\0&0&c&-is\\0&0&-is&c
\end{pmatrix},\qquad
CR_Y(\theta)=\begin{pmatrix}
1&0&0&0\\0&1&0&0\\0&0&c&-s\\0&0&s&c
\end{pmatrix},
$$

$$
CR_Z(\theta)=\operatorname{diag}(1,1,e^{-i\theta/2},e^{i\theta/2}).
$$

For multiple controls, use $C^n(R_A(\theta))$; for patterns or equality, substitute $U=R_A(\theta)$ into the corresponding projector formula. The same X wrappers and XOR/uncompute rules apply.

```python
import math

network = circuit()
controls = qRegister(network, size=2)
target = qubit(network)
target.rotateZif(controls, angle=math.pi / 3, where="01")
# Records X on controls[0], a two-control RZ(pi/3), then X on controls[0].
```

These operations require Qiskit export for execution in the current version. Special angles are not automatically converted to stored fixed gates.

**Controlled phases are not controlled RZ rotations.** For example, CT is $\operatorname{diag}(1,1,1,e^{i\pi/4})$, whereas $CR_Z(\pi/4)$ is $\operatorname{diag}(1,1,e^{-i\pi/8},e^{i\pi/8})$. Unlike the single-qubit T/RZ relationship, the difference is not a global phase on the full two-qubit system. If replacing CT with $CR_Z(\pi/4)$, an additional $\operatorname{diag}(1,e^{i\pi/8})$ on the control would be needed. `quarterPhaseIf` exports the controlled T gate directly and needs no such correction.

<a id="47-register-target"></a>

### 4.7 A register as the target

A controlled method on a `qRegister` applies the chosen gate to every target qubit under the same condition. It does not pair target position 0 with control position 0, position 1 with position 1, and so on.

```python
network = circuit()
controls = qRegister(network, size=2)
targets = qRegister(network, size=3)
targets.flipIf(controls, where="01")
```

Without `ancilla`, this loops over the targets and performs the complete conditional operation separately for each one. Here it records three CCX gates and six X wrappers. The input controls must be separate from every target; for equality conditions, keep the reference operand separate from the targets as well.

For $m$ target qubits and a condition projector $\Pi$ on the input subsystem, the combined ideal matrix is:

$$
V=(I-\Pi)\otimes I_{2^m}+\Pi\otimes U^{\otimes m}.
$$

The same formula applies to rotations, using the supplied angle on each target. To control each target by a different qubit, express that explicitly:

```python
for control, target in zip(controls, targets):
    target.flipIf(control)
```

`zip` processes only the shorter length; use equally sized registers when every target should have a paired control. Pairwise CX gates and a register-wide condition represent different operations.

<a id="48-ancilla"></a>

### 4.8 Compute, use, and uncompute with `ancilla`

For a register target, `ancilla` provides one workspace qubit that holds the condition while the target operations are applied. It works with all five fixed controlled methods and all three controlled rotations.

**Required setup:** use a separate qubit in $|0\rangle$, from the same circuit. It must not occur in the controls, equality references, or target register. Keep every condition input separate from the targets so that acting on the targets cannot change the predicate. Qitker checks several structural errors, but it does not verify the ancilla's actual state or enforce every overlap restriction in this construction. These are caller preconditions. `measured=False` is useful for workspace but does not initialize or clean it by itself.

```python
network = circuit()
controls = qRegister(network, size=2)
targets = qRegister(network, size=3)
helper = qubit(network, initialize=0, measured=False)
targets.halfPhaseIf(controls, where="01", ancilla=helper)
```

The generated circuit is equivalent to this alternative construction:

```python
helper.flipIf(controls, where="01")  # Compute the condition into helper.
for target in targets:
    target.halfPhaseIf(helper)       # Use helper as a single control.
helper.flipIf(controls, where="01")  # Uncompute; restore helper to |0>.
```

The uncompute step repeats the conditional X on the helper. It does not undo the S gates applied to the targets.

For a computational-basis input $x$, a predicate $f(x)\in\{0,1\}$, and target state $|\psi\rangle$, the ideal action is:

$$
|x\rangle|0\rangle_a|\psi\rangle
\longmapsto |x\rangle|f(x)\rangle_a|\psi\rangle
\longmapsto |x\rangle|f(x)\rangle_a
\bigl(U^{\otimes m}\bigr)^{f(x)}|\psi\rangle
\longmapsto |x\rangle|0\rangle_a
\bigl(U^{\otimes m}\bigr)^{f(x)}|\psi\rangle.
$$

This extends linearly to superpositions. The assisted and direct circuits agree on the subspace where the helper begins in zero; they need not have the same full unitary for arbitrary helper inputs. Beginning with helper state one reverses the activation condition in this construction. An arbitrary helper state can leave unwanted correlations. Exact cleanup describes the ideal circuit; an approximate anyonic implementation can introduce errors and leakage.

To reuse the condition for a rotation, write, for example, `targets.rotateYif(controls, angle=theta, where="01", ancilla=helper)`. An equality expression can likewise replace `control` and `where`, as in `targets.flipIf(left == right, ancilla=helper)`.

**When it helps.** If a conditional gate on one target expands to $B_U$ logical operations, direct application to $m$ targets uses $mB_U$ operations. The assisted path uses $2B_X+m$: two evaluations of the condition into the helper plus one singly controlled U per target. For a static pattern with $z$ zero positions, $B_U=B_X=2z+1$. For equality between disjoint width-$n$ operands, $B_U=B_X=4n+1$. These count recorded logical operations, not primitive Qiskit decompositions, braids, or execution time. An ancilla is therefore not automatically cheaper, especially for simple conditions or small target registers.

**It does not bypass backend limits.** Computing a condition with three active controls into the helper still creates a three-control X gate. No automatic decomposition into gates with at most two controls is performed by this API.

<a id="49-translation"></a>

### 4.9 Gate translation and execution support

There are two distinct translation stages: Qitker expands patterns, comparisons, and ancilla constructions into logical operations; the exporter then converts each recorded operation to Qiskit. Further decomposition by Qiskit's `transpile` is separate.

| Recorded operation | Exported Qiskit operation |
| --- | --- |
| X with one control | `qc.cx(control, target)` |
| X with two or more controls | `qc.mcx(controls, target)` |
| Y, Z, S, or T with $n$ controls | The corresponding `YGate`, `ZGate`, `SGate`, or `TGate`, followed by `.control(n)` and appended with `controls + [target]`. |
| RX, RY, or RZ with $n$ controls | The corresponding `RXGate(angle)`, `RYGate(angle)`, or `RZGate(angle)`, followed by `.control(n)`. |
| X wrappers and unconditional gates | Ordinary single-qubit gates. |

The current controlled-gate families do not include controlled H, arbitrary user-supplied U, or a dedicated controlled-SWAP method. The symbol U in this chapter describes the mathematics of the supported families, not an additional `controlledU` API.

| Construction | Version 1 anyonic execution | Qiskit export |
| --- | --- | --- |
| Controlled X/Y/Z/S/T with one or two active controls | Stored CX/CY/CZ/CS/CT and CCX/CCY/CCZ/CCS/CCT braid sequences. | Supported. |
| The same gates with more than two active controls | Unsupported. | Supported. |
| Controlled RX/RY/RZ, including special or zero angles | Unsupported. | Supported. |
| `where`, equality, register targets, and `ancilla` | Supported only if every generated gate is supported. | Supported for valid inputs to the described APIs. |

For example, `where="1xx0"` has only two active controls and can produce a supported fixed gate, even though four controls were supplied. Equality between two disjoint three-qubit registers produces a three-control target gate and exceeds the anyonic limit. The restriction concerns each generated gate, not the total number of qubits in the circuit.

<a id="410-validation"></a>

### 4.10 Validation and common mistakes

| Input or usage | Result or correction |
| --- | --- |
| Empty controls, duplicate controls, a target used as a control, or qubits from different circuits | `ValueError`; use distinct condition inputs belonging to the target's circuit. |
| Unsupported control type, a non-qubit list element, or boolean `where` | `TypeError`. |
| Wrong pattern length, invalid pattern characters, or an integer outside the pattern's range | `ValueError`. |
| Quantum comparison of different widths, partial overlap, or a target used as a reference | `ValueError`. |
| Quantum comparison mixing a bare qubit with a list | `TypeError`; use qubit/qubit or equally sized list/list operands. |
| Equality expression plus explicit `where` | `TypeError`; use one condition form. |
| `ancilla` is neither `None` nor a qubit | `TypeError`. |
| Ancilla is also a target qubit | `ValueError`; allocate separate workspace. |
| `ancilla` passed to a qubit-target method, or `where` passed to a `cx`/`CX`-style alias | Unsupported keyword; use the appropriate signature. |
| A qubit initialized to one used as a control | Its current quantum state controls the gate; initialization does not freeze its value. |

Validation occurs while operations are constructed. Register loops and ancilla paths are not transactional: an error discovered later can leave earlier operations appended. Do not assume a failed call rolled the circuit back; correct the input and rebuild an affected circuit when necessary.

For a measured classical decision, use a selected measurement value and ordinary Python code. For a coherent condition inside the circuit, use the controlled methods described here. These are different stages of the program.

## 5. Execution, measurement, and results

The methods in this chapter run Qitker's anyonic simulator. They compare the physical braid output with the ideal logical circuit and sample the resulting state. Exporting to Qiskit is a separate path: external execution does not populate Qitker's measurement report or selected values.

<a id="51-execution"></a>

### 5.1 Execute or measure a circuit

| Method | Behavior | Return value |
| --- | --- | --- |
| `network.execute()` | Creates a fresh anyonic execution and applies the recorded circuit. Does not sample outcomes or create a measurement report. | `None` |
| `network.measure(shots=1024)` | Executes the circuit, samples its final state, filters the measured qubits, and creates a report. | A `reporterObject` instance. |

Use `measure()` when you want results; calling `execute()` immediately before it would execute the circuit twice. Each call starts a new simulation from the logical all-zero state and applies the recorded operations, including any initialization X gates. It does not continue from a previous sampled outcome.

```python
from qitker import circuit, qubit, qRegister

network = circuit()
data = qRegister(network, size=2)
data[0].mix()
data[1].flipIf(data[0])

result = network.measure(shots=1024)
print(result)
```

This prints the report for an approximate anyonic Bell-state preparation. `shots` specifies how many outcomes to sample; pass a positive integer. The simulator executes the braids once per `measure()` call and samples the resulting probability distribution repeatedly. Individual shots do not re-run the braids or overwrite the statevector with a collapsed sample. There is no mid-circuit measurement or reset operation in this circuit-building API.

<a id="52-counts"></a>

### 5.2 Counts, measured qubits, and shots

```python
counts = result.getPercentageOpbject()
print(counts)
print(result.getPercentage())
```

The spelling `getPercentageOpbject` is the current API name. It returns a dictionary mapping bitstrings to integer **shot counts**, not percentages. `getPercentage()` returns formatted text with counts and percentages; its rows are ordered by binary value, followed by `LEAKAGE` when present.

For an outcome $b$ and $N$ shots, the empirical probability is $\widehat p(b)=\text{counts}[b]/N$. Only observed outcomes appear in the dictionary; use `counts.get(bitstring, 0)` when an outcome may be absent. Counts sum to the requested number of shots, including any `LEAKAGE` count. Percentages use this same total, rather than only the non-leakage shots.

The simulator initially decodes full-system outcomes. Qitker then retains only positions whose `measured` flag is `True`, in circuit creation order, and merges counts with the same retained bitstring. For example, with only positions 0 and 2 measured, full outcomes `000` and `010` both contribute to reported `00`. The special `LEAKAGE` label remains unchanged.

`measured=False` suppresses output bits; it does not remove helper qubits from the simulated state, the fidelity comparison, or the leakage calculation. It also does not reduce the physical state-space dimension.

More shots reduce sampling fluctuations, typically at a rate proportional to $1/\sqrt{N}$. They do not improve the braid approximation, remove leakage, or guarantee the algorithm's desired answer. Qitker does not expose a `seed` parameter on `measure()`.

<a id="53-selection"></a>

### 5.3 Select an outcome and read values

| Call | Meaning | Return value |
| --- | --- | --- |
| `result.getOutcome(rank=1)` | Looks up the ranked non-leakage outcome without selecting it. | Bitstring (`str`). |
| `result.selectResult(rank=1)` | Selects that outcome as the circuit's current result. | Bitstring (`str`). |
| `q.getValue()` | Reads this measured qubit's bit from the selected outcome. | Integer `0` or `1`. |
| `register.getBitstring()` | Reads all register bits in register order. | Binary `str`, preserving leading zeros. |
| `register.getValue()` | Interprets that register bitstring as a binary integer. | `int`. |
| `network.getSelectedValue(q)` | Circuit-level accessor used by `q.getValue()`. Supply a measured qubit belonging to this circuit. | Integer `0` or `1`. |

Ranking starts at 1, sorts by descending shot count, excludes `LEAKAGE`, and breaks ties by the smaller binary integer. It ranks the outcomes actually observed, not all possible bitstrings. Selection does not validate whether an outcome solves the algorithm's problem.

Continuing the Bell example:

```python
best = result.selectResult(rank=1)
print(best)
print(data[0].getValue())
print(data[1].getValue())
print(data.getBitstring())
print(data.getValue())
```

If `best` is `"00"`, the register's integer value is 0; if it is `"11"`, the value is 3. These are examples of decoding, not a guarantee about a particular sampled run.

Neither selecting an outcome nor calling `getValue()` performs another measurement or changes the simulated quantum state. Selection only determines which recorded classical result the accessors read. All qubits read by a register accessor must have been included in measurement. If every shot leaked, there is no non-leakage outcome to select and `getOutcome()`/`selectResult()` raise `ValueError`.

<a id="54-report"></a>

### 5.4 Measurement report API

Obtain the report from `measure()`; it is not one of the three classes imported from the package root. Besides the outcome methods above, it provides:

| Method | Return type | Meaning |
| --- | --- | --- |
| `getPercentageOpbject()` | `dict[str, int]` | Observed outcome counts, possibly including `"LEAKAGE"`. |
| `getPercentage()` | `str` | Formatted counts and percentages. |
| `getShotsNumber()` | `int` for ordinary integer input | Requested number of samples. |
| `getFidelity()` | `str` | Output-state fidelity formatted as a percentage with six decimal places, such as `"99.950000%"`. |
| `getLeakageProbability()` | `float` | State-derived leakage probability from 0 to 1. |
| `getNumberOfAnyons()` | `int` | Four times the circuit's total qubit count, including helpers. |
| `getTotalGates()` | `int` | Recorded logical operations excluding barriers; includes initialization and expanded constructions. |
| `getTotalBraids()` | `int` | Executed braid-generator applications, including routing and inverse routing. This is not the number of low-level F/R steps. |
| `getExecutionTime()` | `float` | Elapsed seconds for execution and sampling, before output filtering and report construction. |
| `getFinalStateVector()` | Complex NumPy array | Full physical fusion-basis statevector before outcome filtering. It is not a logical vector of length $2^n$ in general. |
| `getAnyonMove()` | `str` | Formatted physical operation history. |
| `report(debug=False)` | `str` | Full report text; `debug=True` also includes operation history and the physical statevector. |

```python
print(result.report(debug=False))  # Same report content as print(result).
print(result.getFidelity())        # Already includes the percent sign.
print(f"Leakage: {result.getLeakageProbability():.2%}")
```

`debug` belongs to `report()`, not to `measure()`. The counts dictionary and final statevector are returned without defensive copying; use `.copy()` before making local modifications. Editing them is not a supported way to change or re-run the circuit. Debug output and statevectors can become large as the physical space grows.

<a id="55-fidelity"></a>

### 5.5 Output-state fidelity

Qitker tracks the ideal logical state produced by the same recorded gate sequence, starting from all zeros. It embeds that ideal state in the physical fusion basis with zero amplitudes on leakage states, then compares it with the actual braided state.

For normalized states, the reported quantity is the **pure-state fidelity**:

$$
F=\left|\langle\psi_{\mathrm{ideal}}^{\mathrm{embedded}}
\mid\psi_{\mathrm{physical}}\rangle\right|^2,
\qquad 0\leq F\leq1.
$$

- $F=1$ means the output states agree up to a global phase.
- $F=0$ means they are orthogonal.
- Fidelity tests amplitudes and relative phases, not just measurement frequencies. For example, the ideal Bell states $(|00\rangle+|11\rangle)/\sqrt2$ and $(|00\rangle-|11\rangle)/\sqrt2$ have identical computational-basis probabilities but zero fidelity with each other.

This is fidelity for the chosen circuit input and final state. It is not an average gate/process fidelity over all possible inputs, nor is it the probability that the algorithm returns a correct solution. An ideal Grover or QAOA circuit may itself assign nonzero probability to undesired outcomes.

Fidelity is calculated from the simulated statevectors, independently of the number of shots. It covers the full system, including unmeasured helpers. `getFidelity()` returns formatted text; if a numerical fraction is needed, `float(result.getFidelity().rstrip("%")) / 100` converts it, subject to the report's rounding.

<a id="56-leakage"></a>

### 5.6 Leakage probability

The anyonic Hilbert space contains the logical computational subspace and additional valid fusion states that do not encode ordinary qubit bitstrings. Leakage is probability outside that computational subspace. It is not an incorrect logical answer such as `01` when the desired answer was `11`.

With $P_{\mathrm{comp}}$ the projector onto the computational subspace and a normalized physical state:

$$
L=1-\langle\psi_{\mathrm{physical}}|P_{\mathrm{comp}}|\psi_{\mathrm{physical}}\rangle
=\sum_{j\in\mathrm{leakage}}|\psi_j|^2.
$$

`getLeakageProbability()` returns this state-derived probability. In contrast, `counts.get("LEAKAGE", 0) / shots` is its empirical estimate from a finite sample. A run may observe no leaked shots even when $L>0$.

```python
counts = result.getPercentageOpbject()
predicted = result.getLeakageProbability()
observed = counts.get("LEAKAGE", 0) / result.getShotsNumber()
print(f"State-derived leakage: {predicted:.2%}")
print(f"Observed leaked shots: {observed:.2%}")
```

The fidelity already includes the loss of overlap caused by leakage: the ideal embedded state has no leakage component. For normalized states,

$$
F\leq1-L.
$$

Do not subtract leakage from fidelity a second time. Zero leakage does not imply perfect fidelity: the state can remain entirely computational while having incorrect amplitudes or phases. Conversely, if the surviving computational component matches the ideal state exactly, fidelity reaches $1-L$.

The backend computes these metrics on the complete system before measurement filtering. Marking a helper `measured=False` does not hide its contribution to leakage or fidelity, and the `LEAKAGE` outcome is not removed when choosing which logical bits to report.

<a id="57-limits"></a>

### 5.7 State-space growth and practical limits

For $n$ logical qubits, there are $2^n$ computational-basis bitstrings. Each added qubit doubles this logical dimension. For a search algorithm these bitstrings may represent candidate answers; more generally, this is the circuit's **state space**, not a braid search performed during execution.

Qitker's current physical encoding uses four Fibonacci anyons per qubit and fixes their total charge to vacuum. It retains both computational and leakage states. The resulting physical dimension is $F_{4n-1}$, where $F_0=0$, $F_1=1$, and $F_{k+1}=F_k+F_{k-1}$ are Fibonacci numbers:

| Total qubits, including helpers | Logical dimension $2^n$ | Physical dimension $F_{4n-1}$ |
| --- | --- | --- |
| 1 | 2 | 2 |
| 2 | 4 | 13 |
| 3 | 8 | 89 |
| 4 | 16 | 610 |
| 5 | 32 | 4,181 |
| 6 | 64 | 28,657 |

As $n$ increases, each extra qubit multiplies the physical dimension by approximately $\varphi^4\approx6.85$, where $\varphi=(1+\sqrt5)/2$. The simulator also stores fusion labels, mappings, intermediate bases, and other metadata, so the amplitude-vector size alone does not describe total memory use. These dimensions are structural counts, not runtime or memory benchmarks.

Three limits should be distinguished:

- **Total circuit size:** the current anyonic backend explicitly rejects more than **10 total qubits**, including unmeasured helpers. This is a code guard, not a promise that every circuit of up to 10 qubits is practical; resources may become limiting much earlier. Circuit construction and Qiskit export do not invoke this backend guard.
- **Gate support:** fixed controlled gates support at most two active controls per generated gate. Parameterized rotations are unsupported by anyonic execution. See [section 4.9](#49-translation) for the gate-family table.
- **Simulation cost:** adding helpers enlarges the physical space even when it reduces logical gate counts. Longer braid sequences and routing add work; increasing `shots` adds sampling work without reducing state-space cost. Exported logical simulation avoids Qitker's full fusion-space representation but still has its own resource limits.

For local experiments, start with small circuits and increase their size gradually. The detailed fusion-space construction and backend performance belong in the backend documentation; the essential API distinction is that a circuit can be valid to build and export yet unsupported or impractical to execute through `measure()`.

<a id="58-errors"></a>

### 5.8 Measurement errors and result lifetime

| Situation | Current behavior |
| --- | --- |
| `execute()` or `measure()` on an empty circuit | `TypeError`. |
| No qubits marked for measurement | `measure()` raises `ValueError` when filtering the sampled output. Mark at least one qubit before running. |
| Non-integer `shots`, or `shots < 1` | `TypeError` or `ValueError`, respectively; validation occurs during sampling, after execution. Pass an ordinary positive integer. |
| More than 10 total qubits in anyonic execution | `ValueError` from the backend size guard. |
| More than two controls on a generated gate | `NotImplementedError` during anyonic execution. |
| Unsupported RX/RY/RZ operation in anyonic execution | Rejected by the backend; export to Qiskit instead. |
| Reading a value before measurement or before result selection | `RuntimeError`. |
| Reading an unmeasured qubit after selecting a result | `ValueError`. |
| Non-integer or boolean `rank` | `TypeError`. |
| `rank < 1` or beyond the observed non-leakage outcomes | `ValueError`. |
| Selecting through a report that is no longer the circuit's current report | `RuntimeError`. |

Adding a qubit or any operation, including a barrier, clears the current measurement and selection. Starting another `measure()` call also clears them. Old reports can still be inspected, but selecting an outcome for the circuit requires its current report. Calling `getOutcome()` alone does not establish a selection.

`execute()` alone creates no new report and does not refresh or clear the stored selection from an earlier measurement. Use `measure()` followed by `selectResult()` when a new set of readable results is needed. The high-level API does not resume evolution from a selected classical outcome.

## 6. Qiskit export and execution paths

Export converts the recorded logical operations into a Qiskit circuit. It does not execute the anyonic backend, search for braids, simulate a device, or sample measurement outcomes. You can then use Qiskit tools to inspect, transform, or simulate the exported circuit.

<a id="61-export"></a>

### 6.1 Export API and dependencies

**Signature:** `network.exportCircuit(name)` → a new `qiskit.QuantumCircuit`.

The only supported target name is the exact string `"qiskit"`:

```python
from qitker import circuit, qubit

network = circuit()
q = qubit(network)
q.mix()
qc = network.exportCircuit("qiskit")
```

The returned circuit contains all Qitker qubits, including unmeasured helpers, and a classical register sized for the qubits marked for measurement. No measurement instructions are added. If no qubits are marked for measurement, the exported circuit has no classical bits; it can still be used for logical state or operator analysis without measurement.

Each export builds a new circuit from the current operation list. Later changes to `network` do not update an existing `qc`, and edits to `qc` do not change `network`. Complete construction before exporting and obtaining the measurement mapping, or export again after a change.

Qiskit is an optional dependency imported when export is requested. For installation, follow the [project instructions](../../README.md#installation). A source installation with the `[qiskit]` extra enables export; the [example requirements](../../requirements.txt) also provide Aer and visualization dependencies. Aer is needed for the sampling example below, but not for export itself.

<a id="62-mapping"></a>

### 6.2 Translation of recorded operations

The exporter walks `getOperationVector()` in order. It preserves each operation's target index, control indices, and rotation angle. Aliases such as `mix()` and `quarterPhase()` have already become H and T records by this stage.

| Qitker operation record | Exported operation |
| --- | --- |
| H, X, Y, Z, S, T | `qc.h(t)`, `qc.x(t)`, `qc.y(t)`, `qc.z(t)`, `qc.s(t)`, `qc.t(t)` respectively. |
| RX, RY, RZ | `qc.rx(angle, t)`, `qc.ry(angle, t)`, `qc.rz(angle, t)`. |
| X with one control | `qc.cx(c, t)`. |
| X with two or more controls | `qc.mcx(controls, t)`. |
| Controlled Y, Z, S, T | Construct the corresponding `YGate`, `ZGate`, `SGate`, or `TGate`; append `.control(n)` on `controls + [t]`. |
| Controlled RX, RY, RZ | Construct `RXGate(angle)`, `RYGate(angle)`, or `RZGate(angle)`; append `.control(n)` on `controls + [t]`. |
| Barrier | `qc.barrier()` across the exported qubits. |

Here, `t` is the target index, `c` a single control index, and `n` the number of controls. Qitker qubit index 0 remains Qiskit qubit index 0: export does not reverse the wires.

Higher-level constructions are already expanded before export:

- Initialization contributes ordinary X gates for initial ones.
- Register operations contribute one operation per target.
- SWAP contributes three CX gates; cyclic shifts contribute the generated SWAP decompositions.
- `where` contributes X wrappers and a gate on the active controls.
- Equality contributes XOR computation, a zero-conditioned gate, and uncomputation.
- An ancilla path contributes compute/use/uncompute operations.

The exporter does not turn these back into their original method calls. Their matrices and decompositions are described in [sections 3](#3-circuit-and-register-operations) and [4](#4-controlled-gates-and-conditions). Qiskit's later `transpile` step may further decompose, combine, or optimize gates for its selected backend; the resulting gate count need not equal Qitker's recorded count.

<a id="63-measurements"></a>

### 6.3 Add the measurement mapping

**Signature:** `network.getMeasuredLists()` → `(quantum_indices, classical_indices)`, a tuple of two Python lists.

The first list contains the circuit-wide indices of qubits marked `measured=True`, in creation order. The second contains consecutive classical destinations `0, 1, ..., m-1`, where `m` is the number of measured qubits.

```python
network = circuit()
first = qubit(network, initialize=1)  # Qubit 0: measured.
helper = qubit(network, measured=False)  # Qubit 1: omitted from measurement.
last = qubit(network)                # Qubit 2: measured.

qc = network.exportCircuit("qiskit")
quantum_indices, classical_indices = network.getMeasuredLists()
# quantum_indices == [0, 2]; classical_indices == [0, 1].
qc.measure(quantum_indices, classical_indices)
```

The compact equivalent is `qc.measure(*network.getMeasuredLists())`. It measures qubit 0 into classical bit 0 and qubit 2 into classical bit 1; helper qubit 1 remains part of the quantum circuit.

`getMeasuredLists()` only returns indices. It does not add instructions, allocate bits, execute a simulation, or select a result. Add the measurements to the exported circuit once, after its gates. With no marked qubits, both lists are empty and there are no selected classical outcomes to sample.

Qiskit methods such as `measure_all()` may introduce a different mapping or extra classical bits. Use the mapping above to preserve the measurement selection defined in Qitker.

<a id="64-aer"></a>

### 6.4 Complete Qiskit Aer example

This standalone example uses a rotation, exports the circuit, adds measurements, and samples it in Aer:

```python
import math
from qitker import circuit, qRegister
from qiskit import transpile
from qiskit_aer import Aer

network = circuit()
data = qRegister(network, size=2)
data[0].rotateY(math.pi / 3)
data[1].flip()

qc = network.exportCircuit("qiskit")
qc.measure(*network.getMeasuredLists())

simulator = Aer.get_backend("qasm_simulator")
compiled = transpile(qc, simulator)
shots = 2048
raw_counts = simulator.run(compiled, shots=shots).result().get_counts()

# Convert Qiskit's displayed classical-bit order to Qitker order.
counts = {bits[::-1]: count for bits, count in raw_counts.items()}
best = max(counts, key=counts.get)
print(counts)
print(f"Most frequent result: {best} ({counts[best]}/{shots} shots)")
```

The ideal state, in Qitker order, is:

$$
\frac{\sqrt3}{2}|01\rangle+\frac12|11\rangle.
$$

Thus the expected probabilities are 75% for `01` and 25% for `11`; sampled counts fluctuate. No noise model is supplied here. Aer simulates the logical rotation and X gate, not their anyonic realization. In particular, this example can execute through export even though its RY gate is unsupported by Qitker's anyonic backend.

<a id="65-decoding"></a>

### 6.5 Decode results and inspect the exported circuit

Qiskit displays a classical register with its highest-index bit on the left. Under Qitker's unchanged measurement mapping, reversing each plain binary key restores measured-qubit creation order. This is a display conversion, not a quantum SWAP or change of the circuit.

For the noncontiguous mapping `[0, 2]` in section 6.3, the prepared values are qubit 0 = 1 and qubit 2 = 0. Qiskit displays `"01"` (classical bit 1, then bit 0); reversing it gives Qitker's `"10"` (qubit 0, then qubit 2). The unmeasured helper has no position in that string.

For a selected Qitker-order bitstring, map bits back to circuit indices explicitly:

```python
# Continue the Aer example from section 6.4, where best is already reversed.
measured_indices, _ = network.getMeasuredLists()
selected_values = {
    index: int(bit)
    for index, bit in zip(measured_indices, best)
}
first_value = selected_values[data[0].getIndex()]
register_bits = "".join(str(selected_values[q.getIndex()]) for q in data)
register_value = int(register_bits, 2)
print(first_value, register_bits, register_value)
```

The register decoding assumes every qubit in that register was measured. An external counts dictionary is not a `reporterObject`: it has no `selectResult()` method. The mapping above does not populate Qitker's internal selection. Calls to `data.getValue()` cannot read this Aer run; they either fail for lack of a selected Qitker result or read a previously selected Qitker result if one exists.

Reversing an entire string is appropriate for the single classical register and mapping produced here. If you add classical registers, change measurement destinations, or receive keys containing register separators, decode according to that revised layout. Also distinguish counts ordering from statevector ordering: a statevector describes all quantum wires, including helpers, rather than only the selected classical bits.

The exported object supports Qiskit's inspection tools:

```python
print(qc.draw(output="text"))
print(qc.count_ops())
```

For optional graphical output, `qc.draw(output="mpl")` and `plot_histogram(counts)` use the visualization dependencies listed in the project README. They belong to Qiskit; Qitker's own `network.draw()` prints its recorded text diagram. Inspection and plotting do not create a Qitker measurement report.

<a id="66-execution-paths"></a>

### 6.6 Choose an execution path

| Capability | `network.measure(...)` | Export and run in Qiskit Aer |
| --- | --- | --- |
| Simulated model | Physical Fibonacci-anyon fusion states and stored braids. | Exported logical gates; any externally configured simulation model belongs to Qiskit/Aer. |
| Fixed controlled gates | Up to two active controls per generated gate. | Multi-controlled gates supported by the exporter and simulator. |
| Rotation angles | Unsupported in current anyonic execution. | Passed to the corresponding logical rotations. |
| Circuit-size constraint | Backend rejects more than 10 total qubits; practical limits can be lower. | Does not invoke Qitker's 10-qubit guard; simulator memory and runtime still limit circuit size. |
| Measurement setup | Uses `measured` flags automatically. | Add `qc.measure(*network.getMeasuredLists())` explicitly. |
| Result object | Qitker report, selection API, and value accessors. | Qiskit result and counts, decoded externally. |
| Qitker fidelity, leakage, and braid history | Included in the report. | Not computed by this path. |

Successful export establishes that the logical circuit was translated; it does not establish that the same circuit can run on the anyonic backend. Likewise, successful logical simulation does not measure braid accuracy. See [section 5](#5-execution-measurement-and-results) for the definitions of Qitker's fidelity, leakage, and physical-space cost.

<a id="67-export-errors"></a>

### 6.7 Export errors and common mistakes

| Situation | Behavior or correction |
| --- | --- |
| `exportCircuit(None)` or another non-string target | `TypeError`. |
| `exportCircuit("Qiskit")`, `"cirq"`, or another unsupported name | `ValueError`; use exactly `"qiskit"`. |
| Qiskit is not installed | Import failure when export is requested; install the optional dependency. |
| Aer is not installed | Export can still work, but importing `qiskit_aer` for simulation fails. |
| Export followed immediately by `get_counts()` without adding measurements | No selected classical outcomes have been recorded; add measurements before sampling. |
| Calling `network.measure()` after export to obtain Aer results | Runs the anyonic backend instead. Run the exported Qiskit circuit through the external simulator. |
| Adding Qitker gates after export | Re-export to include those gates. Obtain the mapping again if the qubit layout changed. |
| Using Qitker `getValue()` to read an Aer outcome | Decode the external bitstring as shown above. |

For larger worked examples of this path, see [constrained Grover search](D3_advanced_grover.md) and [Sudoku with QAOA](D4_sudoku3x3.md).

## 7. API index and technical appendix

<a id="71-scope"></a>

### 7.1 Scope and constructors

This index covers the named methods exposed by `circuit`, `qubit`, `qRegister`, and the measurement report, including aliases and construction hooks. It also explains the operation records returned by circuit inspection. Physical-engine classes, research scripts, and general Qiskit APIs are outside this frontend reference.

Import the three core classes with `from qitker import circuit, qubit, qRegister`. Signatures below omit Python's implicit `self` argument. Names are case-sensitive. Grouped aliases retain their exact spelling; each listed alias is a separate callable name.

| Constructor | Creates | Reference |
| --- | --- | --- |
| `circuit()` | An empty circuit. | [Circuit](#12-circuit) |
| `qubit(quantumCircuit, initialize=0, measured=True)` | One newly allocated qubit. | [Qubit initialization](#13-qubit) |
| `qRegister(quantumCircuit, size=None, initialize=0, measured=True)` | An ordered group of newly allocated qubits. | [Register initialization](#14-qregister) |

Obtain a measurement report through `measure()` rather than constructing one manually. Likewise, normal gate methods create their operation records automatically. Methods beginning with a single underscore are implementation helpers and are not entry points in this reference.

<a id="72-circuit-index"></a>

### 7.2 Circuit method index

| Signature | Return value / purpose | Reference |
| --- | --- | --- |
| `addOperation(op)` | `None`; appends an operation record. Construction hook. | [Technical appendix](#77-internals) |
| `addQubit(qubit)` | `None`; registers an object in the circuit. Construction hook. | [Technical appendix](#77-internals) |
| `barrier()` | `None`; adds a full-circuit barrier. | [Barrier](#34-barrier) |
| `details()` | `None`; prints circuit metadata and diagram. | [Text information](#35-drawing-and-text-information) |
| `draw()` | `None`; prints the text circuit diagram. | [Drawing](#35-drawing-and-text-information) |
| `execute()` | `None`; performs a fresh anyonic execution without sampling. | [Execution](#51-execution) |
| `exportCircuit(name)` | A new Qiskit `QuantumCircuit` for `name="qiskit"`. | [Export](#61-export) |
| `filtered(measureOutput)` | A new counts dictionary retaining selected bits and leakage. Internal measurement helper. | [Technical appendix](#77-internals) |
| `getIndex(qubit)` | The qubit's circuit-wide index. | [Circuit inspection](#36-inspecting-circuit-structure) |
| `getMeasuredLists()` | Tuple of quantum-index and classical-index lists. | [Measurement mapping](#63-measurements) |
| `getOperationVector()` | NumPy array of recorded operations. | [Operation inspection](#36-inspecting-circuit-structure) |
| `getQubitsArray()` | List of the circuit's qubit objects. | [Circuit inspection](#36-inspecting-circuit-structure) |
| `getQubitsNumber()` | Total qubit count, including helpers. | [Circuit inspection](#36-inspecting-circuit-structure) |
| `getQubitsNumberToMeasure()` | Count of qubits marked for measurement. | [Circuit inspection](#36-inspecting-circuit-structure) |
| `getSelectedValue(currentQubit)` | Integer bit from the selected measurement outcome. | [Selection and values](#53-selection) |
| `measure(shots=1024)` | A new measurement report from anyonic execution. | [Measurement](#51-execution) |

<a id="73-shared-index"></a>

### 7.3 Shared qubit and register methods

Each gate method in this table returns `None`. On a register it acts on every qubit; metadata and value accessors have different return shapes as indicated.

| Signature or complete alias group | Meaning | Reference |
| --- | --- | --- |
| `getIndex()` | Qubit: integer index. Register: list of indices. | [Object information](#15-register-access-and-object-information) |
| `getValue()` | Qubit: selected bit. Register: selected binary value as an integer. | [Selection and values](#53-selection) |
| `H()`, `h()`, `mix()`, `superPosition()` | Hadamard gate. | [H matrix](#22-hadamard) |
| `isToMeasure()` | Qubit: boolean flag. Register: list of flags. | [Object information](#15-register-access-and-object-information) |
| `rotateX(angle)`, `RX(angle)` | X-axis rotation in radians. | [RX matrix](#28-rx) |
| `rotateY(angle)`, `RY(angle)` | Y-axis rotation in radians. | [RY matrix](#29-ry) |
| `rotateZ(angle)`, `RZ(angle)` | Z-axis rotation in radians. | [RZ matrix](#210-rz) |
| `S()`, `s()`, `halfPhase()` | S gate; relative phase of pi/2. | [S matrix](#26-s-gate) |
| `T()`, `t()`, `quarterPhase()` | T / pi-over-eight gate; relative phase of pi/4. | [T matrix](#27-t-gate) |
| `X()`, `x()`, `flip()` | Pauli-X / bit-flip gate. | [X matrix](#23-pauli-x) |
| `Y()`, `y()`, `flipPhase()` | Pauli-Y gate. | [Y matrix](#24-pauli-y) |
| `Z()`, `z()`, `phase()` | Pauli-Z / phase-flip gate. | [Z matrix](#25-pauli-z) |

For a method named by an alias rather than its professional gate name, follow the same matrix link. In particular, `phase()` is Z, `halfPhase()` is S, and `quarterPhase()` is T; they are not arbitrary-angle rotation methods.

<a id="74-controlled-index"></a>

### 7.4 Controlled method signatures and aliases

These methods return `None`. Their conditions, matrices, and gate expansions are described in [section 4](#4-controlled-gates-and-conditions).

| Gate family | Signature on `qubit` | Signature on `qRegister` |
| --- | --- | --- |
| Controlled X | `flipIf(control, where=None)` | `flipIf(control, where=None, ancilla=None)` |
| Controlled Y | `flipPhaseIf(control, where=None)` | `flipPhaseIf(control, where=None, ancilla=None)` |
| Controlled Z | `phaseIf(control, where=None)` | `phaseIf(control, where=None, ancilla=None)` |
| Controlled S | `halfPhaseIf(control, where=None)` | `halfPhaseIf(control, where=None, ancilla=None)` |
| Controlled T | `quarterPhaseIf(control, where=None)` | `quarterPhaseIf(control, where=None, ancilla=None)` |
| Controlled RX | `rotateXif(control, angle=0, where=None)` | `rotateXif(control, angle, where=None, ancilla=None)` |
| Controlled RY | `rotateYif(control, angle=0, where=None)` | `rotateYif(control, angle, where=None, ancilla=None)` |
| Controlled RZ | `rotateZif(control, angle=0, where=None)` | `rotateZif(control, angle, where=None, ancilla=None)` |

The following aliases exist only on a `qubit` target and accept `control` alone:

| Signatures | Equivalent method | Reference |
| --- | --- | --- |
| `cs(control)`, `CS(control)` | `halfPhaseIf(control)` | [CS](#42-one-control) |
| `ct(control)`, `CT(control)` | `quarterPhaseIf(control)` | [CT](#42-one-control) |
| `cx(control)`, `CX(control)` | `flipIf(control)` | [CX / CNOT](#42-one-control) |
| `cy(control)`, `CY(control)` | `flipPhaseIf(control)` | [CY](#42-one-control) |
| `cz(control)`, `CZ(control)` | `phaseIf(control)` | [CZ](#42-one-control) |

Quick lookup: [multiple controls / Toffoli](#43-multiple-controls), [patterns and `where`](#44-where), [equality `==`](#45-equality), [controlled rotations](#46-controlled-rotations), [register targets](#47-register-target), and [ancilla requirements](#48-ancilla).

<a id="75-object-index"></a>

### 7.5 Object-specific methods and Python syntax

| Owner | Signature | Return value / purpose | Reference |
| --- | --- | --- | --- |
| `qubit` | `swap(control)` | `None`; exchanges quantum contents with another qubit through three CX gates. | [SWAP](#32-swap) |
| `qRegister` | `getBitstring()` | Selected register value as a binary string. | [Selection and values](#53-selection) |
| `qRegister` | `getQubit(index)` | Existing qubit at the requested register position. | [Register access](#15-register-access-and-object-information) |
| `qRegister` | `shiftLeft(amount=1)` | `None`; cyclic left shift of quantum contents. | [Cyclic shifts](#33-cyclic-shifts) |
| `qRegister` | `shiftRight(amount=1)` | `None`; cyclic right shift of quantum contents. | [Cyclic shifts](#33-cyclic-shifts) |

Python syntax reaches additional special methods:

| Syntax | Implementation / behavior | Reference |
| --- | --- | --- |
| `register[index]`, `register[start:stop:step]` | `qRegister.__getitem__(key)` returns a qubit or a list of existing qubits. | [Register access](#15-register-access-and-object-information) |
| `for q in register` | Iteration through indexed access; no separate `__iter__` method is defined. | [Register access](#15-register-access-and-object-information) |
| `left == right` | `qubit.__eq__(other)` or `qRegister.__eq__(other)` creates an equality condition for supported operand types. | [Equality](#45-equality) |
| `str(obj)`, `print(obj)` | The core objects' `__str__()` methods provide text metadata. Register string conversion also prints its qubits' metadata. | [Text information](#35-drawing-and-text-information) |
| `repr(obj)` | The core objects' `__repr__()` methods use their string implementations. | [Text information](#35-drawing-and-text-information) |
| `str(result)`, `print(result)` | The report's `__str__` returns `report()` text. Use `result.report(debug=True)` for debug output. | [Report API](#54-report) |
| `hash(q)`, `hash(register)` | `__hash__` is inherited explicitly from `object`; it identifies Python objects, not quantum values. | [Object identity](#77-internals) |

There is no `len(register)` implementation; use `len(register[:])`. Use `is` to test whether two references are the same Python object. Quantum equality conditions belong inside controlled methods, not in ordinary Python control flow.

<a id="76-report-index"></a>

### 7.6 Measurement report index

The report returned by `network.measure()` exposes the following named methods, in alphabetical order:

| Signature | Return value / purpose | Reference |
| --- | --- | --- |
| `getAnyonMove()` | String containing formatted physical operation history. | [Report API](#54-report) |
| `getExecutionTime()` | Elapsed execution and sampling time in seconds. | [Report API](#54-report) |
| `getFidelity()` | Output-state fidelity as formatted percentage text. | [Fidelity](#55-fidelity) |
| `getFinalStateVector()` | Complex NumPy array in the full physical fusion basis. | [Report API](#54-report) |
| `getLeakageProbability()` | State-derived leakage probability as a float. | [Leakage](#56-leakage) |
| `getNumberOfAnyons()` | Total number of anyons: four per allocated qubit. | [Report API](#54-report) |
| `getOutcome(rank=1)` | Ranked non-leakage bitstring, without selecting it. | [Selection](#53-selection) |
| `getPercentage()` | Formatted shot counts and percentages. | [Counts](#52-counts) |
| `getPercentageOpbject()` | Outcome-count dictionary; spelling preserved from the API. | [Counts](#52-counts) |
| `getShotsNumber()` | Requested shot count. | [Report API](#54-report) |
| `getStructure()` | Nested tuple of anyon IDs describing the final fusion-tree topology. | [Structure details below](#76-structure) |
| `getTotalBraids()` | Executed braid-generator count, including routing. | [Report API](#54-report) |
| `getTotalGates()` | Recorded logical gate count, excluding barriers. | [Report API](#54-report) |
| `report(debug=False)` | Full report text. | [Report API](#54-report) |
| `selectResult(rank=1)` | Selects and returns a ranked non-leakage bitstring. | [Selection](#53-selection) |

<a id="76-structure"></a>

**Fusion-tree structure.** `getStructure()` returns the nested tuple produced by the physical tree's `to_ids()` when the report is created. Integer leaves are anyon identities, not qubit indices, measured bits, or fusion-charge labels. For example, a one-qubit circuit with no gates has structure `((1, 2), (3, 4))`. Braiding can change the order and grouping represented by the final tree. The tuple describes topology; it does not contain state amplitudes or the complete fusion-basis labels needed to interpret every statevector entry.

```python
from qitker import circuit, qubit

network = circuit()
qubit(network)
result = network.measure(shots=1)
print(result.getStructure())  # ((1, 2), (3, 4)) for this no-gate example.
```

The current `report(debug=True)` also includes this structure, followed by operation history and the physical statevector. Obtain these components separately through their getters when you need to process them rather than read the formatted report.

<a id="77-internals"></a>

### 7.7 Construction hooks and operation records

The following hooks are callable on `circuit`, but ordinary programs should use constructors and gate methods, which maintain the intended circuit structure.

**`addQubit(qubit)` → `None`.** Appends the supplied object to the circuit's qubit list, increments the count, and clears the current measurement and selection. It does not create a qubit or assign its `_index`; the `qubit` constructor handles that sequence. Calling `addQubit()` again on an already registered qubit duplicates the registration. It does not validate type, ownership, or duplication, so it is not a way to move qubits between circuits.

**`addOperation(op)` → `None`.** Appends an operation object to the NumPy operation vector and clears the current measurement and selection. It does not validate a gate name, target index, control list, or angle. Normal gate methods construct these records and perform the relevant frontend checks. Do not pass arbitrary gate strings, Qiskit gate objects, or records with invalid indices and expect this hook to validate or translate them.

**`filtered(measureOutput)` → `dict[str, int]`.** Takes full-system Qitker-order counts, keeps the positions marked for measurement, merges equal retained keys, and preserves `"LEAKAGE"`. It returns a new dictionary without selecting a result, creating a report, or running a simulation. It raises `ValueError` if no qubits are marked for measurement. It assumes well-formed full-width input keys and counts; it is not a general input validator or an Aer bit-order converter. See [measurement filtering](#52-counts).

**Operation record types.** These are defined in `qitker.compiler.operations.opClasses`; they are not exported from the package root. `getOperationVector()` returns instances of these classes:

| Record constructor | Fields accessible through getters |
| --- | --- |
| `opType(gateName)` | `getName()`; used for a barrier. |
| `gateOpType(gateName, target)` | `getName()`, `getTarget()`. |
| `controlledOpType(gateName, target, controllers)` | `getName()`, `getTarget()`, `getControllers()`. |
| `rotateOpType(gateName, target, angle=0)` | `getName()`, `getTarget()`, `getAngle()`. |
| `controlledRotateOpType(gateName, target, controllers, angle=0)` | `getName()`, `getTarget()`, `getControllers()`, `getAngle()`. |

Targets and controllers are circuit-wide integer indices, not `qubit` objects. The getters return the stored fields; `getControllers()` returns the stored list without copying it. The records' string representations describe those fields. Creating a record alone does not append it to a circuit or validate backend support. For supported inspection code that accounts for record types, see [section 3.6](#36-inspecting-circuit-structure).

**Equality and identity.** The `EqualityCondition` helper in `qitker.compiler.qubit` stores the left and right operands of `==`. Its construction is normally handled by the operator overload; it is not a package-root API. Its `__bool__()` checks whether those operands are the same Python object. Hashes, object identity, and Python list comparisons therefore must not be interpreted as comparisons of quantum values. Use the supported [condition forms](#45-equality) to construct quantum comparisons.

Internal dispatch such as `_controlledGate`, `_controlledRotateGate`, and `_selectMeasurementOutcome`, the `operation.apply_*` construction helpers, and direct manipulation of underscore-prefixed attributes belong to the implementation. The callable names indexed above cover the frontend objects and returned records; they do not imply that every internal helper is a supported user extension point.

<a id="78-troubleshooting"></a>

### 7.8 Troubleshooting and support lookup

| Symptom or question | First check | Reference |
| --- | --- | --- |
| Cannot find a familiar gate name | Look up its alias group; for example, T is `quarterPhase`, and Toffoli is `flipIf` with two controls. | [Single-qubit index](#73-shared-index), [controlled index](#74-controlled-index) |
| A method rejects `where` or `ancilla` | Check its exact signature and target type. `ancilla` is available on register-target controlled methods. | [Controlled signatures](#74-controlled-index) |
| A register condition activates on the wrong bits | Check control-list order, pattern width, and integer padding. Integer 1 is not an all-ones pattern. | [`where`](#44-where) |
| A Python `if` or list comparison gives an unexpected result | Quantum `==` conditions are inputs to controlled methods, not measurement queries. | [Equality](#45-equality) |
| `getValue()` fails or returns an older result | Measure through Qitker and select a current outcome; decode Aer results separately. | [Result lifetime](#58-errors), [external decoding](#65-decoding) |
| Counts appear reversed after export | Use the unchanged Qitker measurement mapping and reverse plain Qiskit keys once. | [Bit-order conversion](#65-decoding) |
| Export works but `measure()` fails | Check generated controls, rotation gates, and the anyonic size guard. | [Gate support](#49-translation), [size limits](#57-limits) |
| More shots do not improve fidelity | Shots affect sampling uncertainty, not the physical output state. | [Fidelity](#55-fidelity), [leakage](#56-leakage) |
| Adding a helper makes a simulation more expensive | Helpers enlarge the full fusion space, including when unmeasured. | [State-space growth](#57-limits) |
| A drawing prints `None` or omits angles | `draw()` prints and returns `None`; inspect rotation records for angles. | [Text information](#35-drawing-and-text-information) |
| A failed gate call leaves a partially changed circuit | Construction is not transactional; fix the input and rebuild when needed. | [Validation](#410-validation) |

Error details are grouped by stage: [initialization](#14-qregister), [controlled operations](#410-validation), [measurement and selection](#58-errors), and [export](#67-export-errors). The [execution-path comparison](#66-execution-paths) summarizes which capabilities belong to the anyonic backend and which require external logical simulation.
