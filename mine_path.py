import minescript as m
import time
import threading

# ------------------------------
# Control Handler
# ------------------------------

m.set_default_executor(m.script_loop)

mining_active = False
script_running = True

def listen_keys():
    global mining_active, script_running
    with m.EventQueue() as eq:
        eq.register_key_listener()
        while script_running:
            event = eq.get()
            if event.type == m.EventType.KEY:
                if (event.key == 'o' or event.key == 79) and event.action == 1:  # O key press
                    mining_active = not mining_active
                    if mining_active:
                        m.echo("Mining STARTED")
                    else:
                        m.echo("Mining STOPPED")
                        # Release keys when toggling off
                        m.player_press_attack(False)
                        m.player_press_forward(False)
                
                elif (event.key == 't' or event.key == 84) and event.action == 1:  # T key press
                    m.echo("Script terminated by user.")
                    script_running = False
                    mining_active = False
                    # Release keys when exiting
                    m.player_press_attack(False)
                    m.player_press_forward(False)
                    break
            event = None

# Start the key listener thread
threading.Thread(target=listen_keys, daemon=True).start()
m.echo("Script started! Press O to toggle mining, T to exit.")


def mine_path():
    global mining_active, script_running
    
    while script_running:
        if not mining_active:
            time.sleep(0.1)
            continue
            
        # Perform mining actions while active
        m.player_press_attack(True)
        m.player_press_forward(True)
        time.sleep(0.1)
    
    # Final cleanup
    m.player_press_attack(False)
    m.player_press_forward(False)
    m.echo("Script ended.")

mine_path()