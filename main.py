import numpy as np
import qutip as qt
import matplotlib.pyplot as plt

# --- 1. CONFIGURACIÓN DEL SISTEMA (N=8) ---
N = 8  # Qubits (Tubulin Dimers)
dim = 2
hbar = 1.0
omega_drive = 2 * np.pi * 0.04  # 40Hz Gamma Drive

# Operadores de identidad y Pauli para N qubits
def get_op(op, idx, n):
    op_list = [qt.qeye(dim)] * n
    op_list[idx] = op
    return qt.tensor(op_list)

# --- 2. HAMILTONIANO RENASCENT-Q ---
# Término de acoplamiento Buehler-style
H_coupling = sum( (0.5 / abs(i-j)**1.5) * get_op(qt.sigmax(), i, N) * get_op(qt.sigmax(), j, N)
                  for i in range(N) for j in range(i+1, N) )

# SUSY Pairing (Super-Symmetry protector)
def get_susy_hamiltonian(n):
    # Q = sqrt(2w) * (a_dag * f + a * f_dag)
    # Aquí simplificado para la interacción efectiva de tubulina
    Q = sum(get_op(qt.sigmap(), i, n) for i in range(n))
    return (Q * Q.dag() + Q.dag() * Q)

H0 = H_coupling + 0.1 * get_susy_hamiltonian(N)

# --- 3. MODULACIÓN ZETA (Ruido Negentrópico) ---
# Simulamos los primeros ceros de Riemann como frecuencias de drive
riemann_zeros = [14.13, 21.02, 25.01, 30.42, 32.93] # Frecuencias imaginarias (impresión zeta)

def zeta_noise(t, args):
    return 0.05 * sum(np.sin(z * t) for z in riemann_zeros)

# Hamiltoniano dependiente del tiempo
H = [H0, [sum(get_op(qt.sigmaz(), i, N) for i in range(N)), zeta_noise]]

# --- 4. EVOLUCIÓN Y MÉTRICAS ---
psi0 = qt.tensor([qt.basis(dim, 0)] * N)  # Estado inicial |000...0>
tlist = np.linspace(0, 50, 500)

# Colapso modulado (Decoherencia biológica)
c_ops = [np.sqrt(0.01) * get_op(qt.destroy(dim), i, N) for i in range(N)]

# Resolver Ecuación Maestra de Lindblad
result = qt.mesolve(H, psi0, tlist, c_ops, [])

# --- 5. CÁLCULO DE NEGENTROPÍA ---
entropies = [qt.entropy_vn(rho) for rho in result.states]
delta_s = entropies[-1] - entropies[0]

print(f"Simulación RENASCENT-Q completada.")
print(f"Variación de Entropía (Delta S): {delta_s:.5f} bits")

# --- 6. PLOT DE RESULTADOS ---
plt.figure(figsize=(10,6))
plt.plot(tlist, entropies, label='Von Neumann Entropy (S)', color='cyan')
plt.title("RENASCENT-Q: Negentropic Dynamics (N=8)")
plt.xlabel("Time (ns)")
plt.ylabel("Entropy (bits)")
plt.grid(True, alpha=0.3)
plt.legend()
plt.show()
