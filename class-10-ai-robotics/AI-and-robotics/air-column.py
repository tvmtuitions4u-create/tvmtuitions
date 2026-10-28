import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ====================== COMMON PARAMETERS ======================
c = 1480.0          # Speed of sound in water (m/s)
L = 10.0            # Length of water column (meters)
Nx = 500            # Number of spatial points
dx = L / (Nx - 1)
dt = 0.4 * dx / c   # Courant number < 0.5 for stability
Nt = 1000           # Number of time steps per simulation

x = np.linspace(0, L, Nx)

# ====================== MAIN SIMULATION FUNCTION ======================
def run_simulation(title, initial_condition, boundary_type, drive_freq=None, layers=False):
    """
    Runs one type of water column simulation
    """
    p = np.zeros(Nx)
    p_prev = np.zeros(Nx)
    
    # Set initial condition
    p[:] = initial_condition
    p_prev[:] = p.copy()

    fig, ax = plt.subplots(figsize=(10, 5))
    line, = ax.plot(x, p, 'b-', linewidth=2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('Position along water column (m)')
    ax.set_ylabel('Acoustic Pressure')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    # Add layer interface if needed
    if layers:
        interface = int(Nx * 0.6)
        ax.axvline(x[interface], color='black', linestyle='--', linewidth=2, label='Layer Interface')
        ax.legend()

    def update(frame):
        nonlocal p, p_prev
        
        p_new = np.zeros(Nx)
        
        # Finite difference update for wave equation
        for i in range(1, Nx-1):
            p_new[i] = 2*p[i] - p_prev[i] - (c*dt/dx)**2 * (p[i+1] - 2*p[i] + p[i-1])
        
        # Apply boundary conditions
        if boundary_type == "open_open":
            p_new[0] = 0
            p_new[-1] = 0
            
        elif boundary_type == "closed_closed":
            p_new[0] = p_new[1]
            p_new[-1] = p_new[-2]
            
        elif boundary_type == "closed_open":
            p_new[0] = p_new[1]      # Closed (rigid)
            p_new[-1] = 0            # Open (pressure release)
            
        elif boundary_type == "layered":
            p_new[0] = 0
            p_new[-1] = 0
            
        elif boundary_type == "driven":
            t = frame * dt
            p_new[0] = 0.8 * np.sin(2 * np.pi * drive_freq * t)   # Driving force
            p_new[-1] = 0

        # Update for next step
        p_prev[:] = p
        p[:] = p_new
        
        line.set_ydata(p)
        return line,

    ani = FuncAnimation(fig, update, frames=Nt, interval=25, blit=True, repeat=False)
    plt.show()
    plt.close()


# ====================== 5 TYPES OF WATER COLUMN SIMULATIONS ======================

print("Starting Sound Wave Simulations in Different Water Columns...\n")

# Type 1: Open-Open
print("1. Open-Open Water Column")
init1 = 0.6 * np.sin(2 * np.pi * x / L)          # Mode 2
run_simulation("Type 1: Open-Open Water Column (Both ends open)", 
               init1, "open_open")

# Type 2: Closed-Closed
print("2. Closed-Closed Water Column")
init2 = 0.6 * np.cos(np.pi * x / L)              # Fundamental mode
run_simulation("Type 2: Closed-Closed Water Column (Both ends rigid)", 
               init2, "closed_closed")

# Type 3: Closed-Open (Most common for water columns)
print("3. Closed-Open Water Column")
init3 = 0.8 * np.cos(np.pi * x / (2 * L))        # Quarter-wave fundamental
run_simulation("Type 3: Closed-Open Water Column (Bottom closed, Surface open)", 
               init3, "closed_open")

# Type 4: Layered Water Column (Different sound speeds)
print("4. Layered Water Column")
c1, c2 = 1520, 1440
interface = int(Nx * 0.6)

def get_local_c(i):
    return c1 if i < interface else c2

# Custom update for layered (different c in different regions)
def run_layered():
    p = np.zeros(Nx)
    p_prev = np.zeros(Nx)
    p[:] = 0.6 * np.sin(3 * np.pi * x / L)
    p_prev[:] = p.copy()

    fig, ax = plt.subplots(figsize=(10, 5))
    line, = ax.plot(x, p, 'm-', linewidth=2)
    ax.axvline(x[interface], color='black', linestyle='--', linewidth=2, label='Layer Interface')
    ax.set_ylim(-1.2, 1.2)
    ax.set_xlabel('Position along water column (m)')
    ax.set_ylabel('Acoustic Pressure')
    ax.set_title("Type 4: Layered Water Column (Different Sound Speeds)")
    ax.grid(True, alpha=0.3)
    ax.legend()

    def update(frame):
        nonlocal p, p_prev
        p_new = np.zeros(Nx)
        
        for i in range(1, Nx-1):
            local_c = get_local_c(i)
            coeff = (local_c * dt / dx)**2
            p_new[i] = 2*p[i] - p_prev[i] - coeff * (p[i+1] - 2*p[i] + p[i-1])
        
        p_new[0] = 0
        p_new[-1] = 0
        
        p_prev[:] = p
        p[:] = p_new
        line.set_ydata(p)
        return line,

    ani = FuncAnimation(fig, update, frames=Nt, interval=25, blit=True, repeat=False)
    plt.show()
    plt.close()

run_layered()

# Type 5: Driven Water Column (Forced oscillation)
print("5. Driven Water Column")
drive_freq = 3 * c / (4 * L)        # Near 3rd resonance of closed-open column
init5 = np.zeros(Nx)
run_simulation(f"Type 5: Driven Water Column (Frequency = {drive_freq:.1f} Hz)", 
               init5, "driven", drive_freq=drive_freq)

print("\nAll 5 simulations completed!")
