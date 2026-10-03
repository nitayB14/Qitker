# Qitker API Reference

[Project overview](D0_Project_Overview.md) · [Installation](../../README.md#installation)

This reference introduces Qitker's circuit-building API in a progressive order. Section 1 covers the core objects, initialization, and register access. Section 2 covers single-qubit gates and rotations, including their matrices and API aliases. Section 3 covers register operations, circuit barriers, drawing, and structural inspection.

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
