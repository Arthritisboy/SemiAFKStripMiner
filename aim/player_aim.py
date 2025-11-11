import time

import minescript as m

def linear_ease(t: float) -> float:
    """Linear easing for fastest movement"""
    return t

def fast_ease_in_out(t: float) -> float:
    """Very fast easing - minimal smoothing"""
    if t < 0.5:
        return 2.0 * t * t
    else:
        t = 2.0 * t - 1.0
        return 0.5 * (1.0 - (1.0 - t) * (1.0 - t)) + 0.5

def smooth_rotate_to(target_yaw: float, target_pitch: float, duration: float = 0.08, step: float = 0.01):
    """ULTRA-FAST smooth rotation with minimal delay"""
    current_yaw, current_pitch = m.player_orientation()
    
    # Normalize angles to handle wraparound
    current_yaw = current_yaw % 360
    target_yaw = target_yaw % 360
    
    # Calculate shortest path for yaw
    yaw_diff = ((target_yaw - current_yaw + 180) % 360) - 180
    pitch_diff = target_pitch - current_pitch
    
    # For very small angles, do instant rotation
    if abs(yaw_diff) < 2.0 and abs(pitch_diff) < 2.0:
        m.player_set_orientation(target_yaw, target_pitch)
        return
    
    steps = max(1, int(duration / step))
    
    for i in range(steps + 1):
        t = i / steps
        # Use linear easing for maximum speed
        f = linear_ease(t)
        
        y = current_yaw + yaw_diff * f
        p = current_pitch + pitch_diff * f
        
        m.player_set_orientation(y % 360.0, p)
        
        # Minimal sleep for fastest movement
        if i < steps:  # Don't sleep on the last step
            time.sleep(step)

def instant_rotate_to(target_yaw: float, target_pitch: float):
    """Instant rotation for when speed is critical"""
    m.player_set_orientation(target_yaw, target_pitch)

def hybrid_rotate_to(target_yaw: float, target_pitch: float, fast_threshold: float = 10.0):
    """Hybrid approach: instant for small moves, fast smooth for larger moves"""
    current_yaw, current_pitch = m.player_orientation()
    
    yaw_diff = abs(((target_yaw - current_yaw + 180) % 360) - 180)
    pitch_diff = abs(target_pitch - current_pitch)
    
    # If the angle change is small, use instant rotation
    if yaw_diff < fast_threshold and pitch_diff < fast_threshold:
        instant_rotate_to(target_yaw, target_pitch)
    else:
        # Use very fast smooth rotation for larger moves
        smooth_rotate_to(target_yaw, target_pitch, duration=0.05, step=0.005)