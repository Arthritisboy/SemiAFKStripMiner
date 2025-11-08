from minescript import *
import time
import math

# Global flag to control the mining loop
mining_active = True
recently_mined_positions = set()  # Track recently mined positions to avoid repeats

def stop_mining():
    global mining_active
    mining_active = False

def check_for_t_press():
    """Check if T key is pressed to stop mining"""
    screen = screen_name()
    if screen and "chat" in screen.lower():
        echo("T pressed! Stopping mining script.")
        stop_mining()
        return True
    return False

def get_ore_blocks_around(position, radius=3):
    """Scan for ore blocks around the given position - EXCLUDE recently mined"""
    ore_blocks = []
    x, y, z = position
    
    # Convert to integers for block scanning
    x, y, z = int(x), int(y), int(z)
    
    # Scan in a cube around the position
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                # Skip the center block and blocks too far
                if dx == 0 and dy == 0 and dz == 0:
                    continue
                    
                check_x, check_y, check_z = x + dx, y + dy, z + dz
                
                # Skip if this position was recently mined
                if (check_x, check_y, check_z) in recently_mined_positions:
                    continue
                    
                block_type = getblock(check_x, check_y, check_z)
                
                if is_ore_block(block_type):
                    ore_blocks.append((check_x, check_y, check_z, block_type))
    
    return ore_blocks

def is_ore_block(block_type):
    """Check if a block is an ore"""
    if not block_type:
        return False
    
    # Remove block states for comparison
    base_block_type = block_type.split('[')[0].split('{')[0].lower()
    
    ore_blocks = {
        "minecraft:coal_ore", "minecraft:deepslate_coal_ore",
        "minecraft:iron_ore", "minecraft:deepslate_iron_ore", 
        "minecraft:gold_ore", "minecraft:deepslate_gold_ore",
        "minecraft:diamond_ore", "minecraft:deepslate_diamond_ore",
        "minecraft:emerald_ore", "minecraft:deepslate_emerald_ore",
        "minecraft:lapis_ore", "minecraft:deepslate_lapis_ore",
        "minecraft:redstone_ore", "minecraft:deepslate_redstone_ore",
        "minecraft:copper_ore", "minecraft:deepslate_copper_ore",
        "minecraft:ancient_debris", "minecraft:nether_gold_ore"
    }
    
    # Check for base ore types
    if base_block_type in ore_blocks:
        return True
    
    # Special case for lit redstone ore
    if "redstone_ore" in base_block_type:
        return True
    
    return False

def mine_ore_vein(start_position, max_blocks=20):
    """Mine an entire ore vein using flood fill algorithm."""
    if not mining_active:
        return 0

    echo(f"Found ore vein! Mining {max_blocks} blocks maximum...")

    mined_blocks = 0
    visited = set()
    queue = [start_position]

    # 26-adjacent directions (3x3x3 cube minus center)
    directions_26 = [(dx, dy, dz) for dx in (-1, 0, 1)
                                 for dy in (-1, 0, 1)
                                 for dz in (-1, 0, 1)
                                 if not (dx == 0 and dy == 0 and dz == 0)]

    while queue and mined_blocks < max_blocks and mining_active:
        # Check for T press
        if check_for_t_press():
            break

        x, y, z = queue.pop(0)

        if (x, y, z) in visited:
            continue

        visited.add((x, y, z))

        block_type = getblock(x, y, z)
        if not is_ore_block(block_type):
            continue

        # Clear path and mine this ore block
        if mine_single_ore_block(x, y, z):
            mined_blocks += 1
            echo(f"Mined ore {mined_blocks}/{max_blocks}: {block_type}")
            
            # Add to recently mined positions
            recently_mined_positions.add((x, y, z))

            # Check all adjacent blocks (including diagonals) for more ore
            for dx, dy, dz in directions_26:
                new_x, new_y, new_z = x + dx, y + dy, z + dz
                if (new_x, new_y, new_z) not in visited:
                    new_block_type = getblock(new_x, new_y, new_z)
                    if is_ore_block(new_block_type):
                        queue.append((new_x, new_y, new_z))

        # Small delay between blocks to avoid spamming inputs
        time.sleep(0.15)

    echo(f"Ore vein mining complete. Mined {mined_blocks} blocks.")
    return mined_blocks

def mine_single_ore_block_simple(x, y, z):
    """Mine a single ore block at the given coordinates"""
    if not mining_active:
        return False
        
    # Check for T press
    if check_for_t_press():
        return False
        
    # Convert to integers
    ore_x, ore_y, ore_z = int(x), int(y), int(z)
    
    echo(f"MINING ORE AT {ore_x}, {ore_y}, {ore_z}")
    
    # Get current position as integers
    current_x, current_y, current_z = player_position()
    current_x, current_y, current_z = int(current_x), int(current_y), int(current_z)
    
    # Calculate direction to look at the ore block
    dx = ore_x - current_x
    dy = ore_y - current_y
    dz = ore_z - current_z
    
    # Calculate yaw and pitch to look at the block
    yaw = math.degrees(math.atan2(-dx, dz))
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    pitch = math.degrees(math.asin(-dy / distance)) if distance > 0 else 0
    
    # Look at the ore block
    player_set_orientation(yaw, pitch)
    time.sleep(0.3)  # Give time for orientation to update
    
    # Get ore type for logging
    ore_type = getblock(ore_x, ore_y, ore_z)
    echo(f"Ore type: {ore_type}")
    
    # Mine the block
    player_press_attack(True)
    
    # Get appropriate mining time
    mine_time = get_mining_time_for_ore(ore_type)
    check_interval = 0.3
    
    ore_mined = False
    start_time = time.time()
    
    while mining_active and (time.time() - start_time) < mine_time:
        # Check for T press
        if check_for_t_press():
            player_press_attack(False)
            return False
            
        # Check if block is still there
        current_block = getblock(ore_x, ore_y, ore_z)
        if not is_ore_block(current_block):
            ore_mined = True
            break
            
        time.sleep(check_interval)
    
    player_press_attack(False)
    
    if ore_mined:
        echo(f"✓ SUCCESS: Mined {ore_type}!")
        # Add to recently mined
        recently_mined_positions.add((ore_x, ore_y, ore_z))
    else:
        echo(f"✗ FAILED: Could not mine {ore_type}")
    
    return ore_mined

def get_mining_time_for_ore(ore_type):
    """Get appropriate mining time for different ore types"""
    if not ore_type:
        return 5.0
    
    ore_lower = ore_type.lower()
    
    if "ancient_debris" in ore_lower:
        return 15.0  # Very tough
    elif "diamond_ore" in ore_lower or "emerald_ore" in ore_lower:
        return 8.0   # Tough
    elif "redstone_ore" in ore_lower:
        return 6.0   # Medium-tough
    elif "gold_ore" in ore_lower or "copper_ore" in ore_lower:
        return 5.0   # Medium
    elif "iron_ore" in ore_lower or "lapis_ore" in ore_lower:
        return 4.0   # Medium
    elif "coal_ore" in ore_lower:
        return 3.0   # Easy
    else:
        return 5.0   # Default
    
def mine_single_block_simple(x, y, z):
    """Simple block mining for path clearing"""
    if not mining_active:
        return False
        
    # Check for T press
    if check_for_t_press():
        return False
        
    # Convert to integers
    x, y, z = int(x), int(y), int(z)
    
    # Calculate direction to block
    current_x, current_y, current_z = player_position()
    current_x, current_y, current_z = int(current_x), int(current_y), int(current_z)
    
    dx = x - current_x
    dy = y - current_y
    dz = z - current_z
    
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance > 5:
        return False
        
    yaw = math.degrees(math.atan2(-dx, dz))
    pitch = math.degrees(math.asin(-dy / distance)) if distance > 0 else 0
    
    # Look at the block
    player_set_orientation(yaw, pitch)
    time.sleep(0.3)
    
    # Mine the block
    player_press_attack(True)
    
    # Check for T press during mining
    start_time = time.time()
    while time.time() - start_time < 1.5 and mining_active:
        if check_for_t_press():
            player_press_attack(False)
            return False
        time.sleep(0.1)
        
    player_press_attack(False)
    time.sleep(0.2)
    
    # Check if block was mined
    return getblock(x, y, z) == "minecraft:air"

def mine_single_ore_block(x, y, z):
    """Main ore mining function - uses simple approach with path clearing"""
    if not mining_active:
        return False
        
    # Check for T press
    if check_for_t_press():
        return False
        
    # Convert to integers
    ore_x, ore_y, ore_z = int(x), int(y), int(z)
    
    # First clear path if needed
    clear_path_to_ore(ore_x, ore_y, ore_z)
    
    # Then mine the ore using simple approach
    return mine_single_ore_block_simple(ore_x, ore_y, ore_z)

def check_for_ores_and_mine(current_position):
    """Check for nearby ores and mine them if found."""
    if not mining_active:
        return False

    # Check for T press
    if check_for_t_press():
        return False

    ore_blocks = get_ore_blocks_around(current_position, radius=2)

    if not ore_blocks:
        return False

    echo(f"Found {len(ore_blocks)} ore blocks nearby!")

    # RELEASE SNEAK when starting ore mining
    player_press_sneak(False)
    echo("Released sneak for ore mining")

    # Save current position and orientation before mining ore veins
    vein_start_position = player_position()
    vein_start_orientation = player_orientation()
    echo(f"Saved position: {vein_start_position}, orientation: {vein_start_orientation}")

    # Sort ores by distance so we mine closest first and reduce reach issues
    px, py, pz = vein_start_position
    ore_blocks.sort(key=lambda b: (b[0]-px)**2 + (b[1]-py)**2 + (b[2]-pz)**2)

    mined_any = False
    mined_this_scan = set()  # Track positions mined in this scan

    for ox, oy, oz, _bt in ore_blocks:
        if not mining_active:
            break
            
        # Check for T press
        if check_for_t_press():
            break
            
        # Skip if we've already mined this position in current scan
        if (ox, oy, oz) in mined_this_scan:
            continue
            
        # Skip if it's no longer an ore (already mined)
        current_bt = getblock(int(ox), int(oy), int(oz))
        if not is_ore_block(current_bt):
            echo(f"Skipping {ox}, {oy}, {oz} - no longer an ore")
            continue

        echo(f"Attempting to mine ore at {ox}, {oy}, {oz}")
        mined_in_vein = mine_ore_vein((int(ox), int(oy), int(oz)))
        if mined_in_vein:
            mined_any = True
            # Add all positions from this vein to our tracking
            mined_this_scan.add((ox, oy, oz))
            # After mining a vein, break and let main loop re-scan
            echo("Vein mined, returning to main mining...")
            break

    # ALWAYS restore original orientation and position after ore mining (successful or not)
    if mining_active:
        echo("Restoring original position and orientation...")
        return_to_position(vein_start_position, vein_start_orientation)

    return mined_any

def clear_path_to_ore(ore_x, ore_y, ore_z):
    """Clear blocks between player and ore - IMPROVED VERSION"""
    if not mining_active:
        return False
        
    # Check for T press
    if check_for_t_press():
        return False
        
    # Convert ore coordinates to integers
    ore_x, ore_y, ore_z = int(ore_x), int(ore_y), int(ore_z)
    
    player_x, player_y, player_z = player_position()
    player_x, player_y, player_z = int(player_x), int(player_y), int(player_z)
    
    echo(f"Clearing path to ore at {ore_x}, {ore_y}, {ore_z}")
    
    # RELEASE SNEAK when clearing path
    player_press_sneak(False)
    echo("Released sneak for path clearing")
    
    # Calculate direction and distance
    dx = ore_x - player_x
    dy = ore_y - player_y  
    dz = ore_z - player_z
    
    distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    if distance > 6:
        echo(f"Ore too far: {distance:.1f} blocks")
        return False
    
    blocks_cleared = 0
    
    # Improved path clearing - only clear blocks that are actually in the way
    # Use Bresenham's line algorithm for better path finding
    steps = max(int(distance * 2), 5)  # More samples for better accuracy
    
    for i in range(1, steps):
        if not mining_active:
            break
            
        # Check for T press
        if check_for_t_press():
            break
            
        # Calculate position along the path with interpolation
        progress = i / (steps - 1)
        check_x = player_x + int(dx * progress)
        check_y = player_y + int(dy * progress)
        check_z = player_z + int(dz * progress)
        
        # Stop if we reach or pass the ore
        if (abs(check_x - ore_x) <= 1 and abs(check_y - ore_y) <= 1 and abs(check_z - ore_z) <= 1):
            break
            
        block_type = getblock(check_x, check_y, check_z)
        
        # If it's a solid block (not air, not ore), mine it
        if (block_type and 
            block_type != "minecraft:air" and 
            not is_ore_block(block_type) and
            "liquid" not in block_type.lower() and
            "bedrock" not in block_type.lower()):
            
            echo(f"Clearing path block: {block_type} at {check_x}, {check_y}, {check_z}")
            
            # Use simple mining for path blocks
            if mine_single_block_simple(check_x, check_y, check_z):
                blocks_cleared += 1
                # Small delay after clearing a block
                time.sleep(0.2)
    
    echo(f"Path clearing complete. Cleared {blocks_cleared} blocks.")
    return blocks_cleared > 0

def return_to_position(target_position, target_orientation):
    """Return to the original position and orientation"""
    if not mining_active:
        return
        
    # Check for T press
    if check_for_t_press():
        return
        
    current_pos = player_position()
    current_ori = player_orientation()
    
    target_x, target_y, target_z = target_position
    current_x, current_y, current_z = current_pos
    
    # Calculate distance to target
    distance = math.sqrt(
        (target_x - current_x)**2 + 
        (target_y - current_y)**2 + 
        (target_z - current_z)**2
    )
    
    # If we're close enough, just set orientation
    if distance < 2:
        player_set_orientation(target_orientation[0], target_orientation[1])
        time.sleep(0.5)
        echo(f"Restored orientation: {target_orientation}")
        return
    
    # Otherwise, look toward target and move
    dx = target_x - current_x
    dz = target_z - current_z
    yaw = math.degrees(math.atan2(-dx, dz))
    
    player_set_orientation(yaw, 0)
    time.sleep(0.5)
    
    # Move toward target
    player_press_forward(True)
    
    while mining_active and distance > 1:
        # Check for T press
        if check_for_t_press():
            player_press_forward(False)
            return
            
        current_pos = player_position()
        current_x, current_y, current_z = current_pos
        
        distance = math.sqrt(
            (target_x - current_x)**2 + 
            (target_y - current_y)**2 + 
            (target_z - current_z)**2
        )
        
        if distance <= 1:
            break
            
        time.sleep(0.1)
    
    player_press_forward(False)
    
    # Set final orientation
    if mining_active:
        player_set_orientation(target_orientation[0], target_orientation[1])
        time.sleep(0.5)
        echo(f"Restored orientation: {target_orientation}")

def check_gravel_block(yaw, pitch=20):
    """Check if the targeted block at given orientation is gravel"""
    if not mining_active:
        return False
        
    # Set orientation to check for gravel
    player_set_orientation(yaw, pitch)
    time.sleep(0.1)
    
    targeted_block = player_get_targeted_block(max_distance=5)
    
    if targeted_block and targeted_block.type:
        return "gravel" in targeted_block.type.lower()
    return False

def gravel_mine():
    """Handle gravel mining with torch placement"""
    if not mining_active:
        return
        
    yaw, pitch = player_orientation()
    
    press_key_bind("key.hotbar.9", True)
    time.sleep(0.2)
    press_key_bind("key.hotbar.9", False)
    
    player_press_attack(True)
    for _ in range(20):
        if not mining_active:
            player_press_attack(False)
            return
        time.sleep(0.1)
    player_press_attack(False)
    
    if mining_active:
        press_key_bind("key.hotbar.1", True)
        time.sleep(0.2)
        press_key_bind("key.hotbar.1", False)

def mine_at_angle(yaw, pitch, check_gravel=True):
    """Mine at specific angle, with optional gravel check"""
    if not mining_active:
        return False
        
    player_set_orientation(yaw, pitch)

    if check_gravel and pitch == 20 and mining_active:
        if check_gravel_block(yaw, pitch):
            gravel_mine()
            return True
    
    if mining_active:
        player_press_attack(True)
        for _ in range(5):
            if not mining_active:
                player_press_attack(False)
                return False
            time.sleep(0.1)
        player_press_attack(False)
    return False

def mining_time():
    global mining_active, original_position, original_orientation, recently_mined_positions
    
    mining_active = True
    recently_mined_positions.clear()  # Clear recent positions on start
    last_chat_check = time.time()
    last_ore_check = time.time()
    
    original_position = player_position()
    original_orientation = player_orientation()
    
    echo("Mining script started with improved ore vein detection!")
    echo("Press T to stop. Will automatically mine ore veins.")
    
    try:
        while mining_active:
            current_time = time.time()
            
            # Check for T press more frequently
            if current_time - last_chat_check > 0.1:
                if check_for_t_press():
                    break
                last_chat_check = current_time
            
            # Check for ores periodically
            if current_time - last_ore_check > 2.0:
                current_pos = player_position()
                ore_detected = check_for_ores_and_mine(current_pos)
                if ore_detected:
                    # If we mined something, wait a bit then continue with regular mining
                    last_ore_check = time.time() + 3.0  # Longer delay after mining
                    continue
                last_ore_check = current_time
            
            # REGULAR MINING MODE - Press sneak for safety
            if mining_active:
                yaw, pitch = player_orientation()
                player_press_sneak(True)
            
            if mining_active:
                player_press_forward(True)
            
            mining_steps = [
                (yaw, 0, False), (yaw, 20, True), (yaw, 0, False), (yaw, 20, True)
            ]
            
            for step_yaw, step_pitch, check_gravel in mining_steps:
                if not mining_active:
                    break
                if check_for_t_press():
                    break
                mine_at_angle(step_yaw, step_pitch, check_gravel)
            
            if mining_active:
                player_press_forward(False)
            
            if mining_active:
                mining_steps_2 = [(yaw, 0, False), (yaw, 20, True)]
                for step_yaw, step_pitch, check_gravel in mining_steps_2:
                    if not mining_active:
                        break
                    if check_for_t_press():
                        break
                    mine_at_angle(step_yaw, step_pitch, check_gravel)
            
            if mining_active:
                yaw, pitch = player_orientation()
            
            if mining_active:
                player_press_forward(True)
            
            if mining_active:
                mining_steps_3 = [(yaw, 0, False), (yaw, 20, True), (yaw, 0, False), (yaw, 20, True)]
                for step_yaw, step_pitch, check_gravel in mining_steps_3:
                    if not mining_active:
                        break
                    if check_for_t_press():
                        break
                    mine_at_angle(step_yaw, step_pitch, check_gravel)
            
            if mining_active:
                player_press_forward(False)
            
            if mining_active:
                mining_steps_4 = [(yaw, 0, False), (yaw, 20, True)]
                for step_yaw, step_pitch, check_gravel in mining_steps_4:
                    if not mining_active:
                        break
                    if check_for_t_press():
                        break
                    mine_at_angle(step_yaw, step_pitch, check_gravel)
            
            if mining_active:
                player_press_forward(True)
                for i in range(3): 
                    if not mining_active:
                        player_press_forward(False)
                        break
                    if check_for_t_press():
                        player_press_forward(False)
                        break
                    time.sleep(0.1)
                if mining_active:
                    player_press_forward(False)
            
            if mining_active:
                echo("Mining cycle complete")
                
    finally:
        # Always release all keys when stopping
        player_press_sneak(False)
        player_press_forward(False)
        player_press_attack(False)
        echo("Mining script stopped completely.")

mining_time()