import numpy as np
from scipy.integrate import solve_ivp
import pygame
import sys

g = 9.81  # grawitacja m/s^2


def equations(t, y, l1, l2, m1, m2):
    theta1, z1, theta2, z2 = y
    c, s = np.cos(theta1 - theta2), np.sin(theta1 - theta2)

    theta1_dot = z1
    theta2_dot = z2

    z1_dot = (m2 * g * np.sin(theta2) * c - m2 * s * (l1 * z1 ** 2 * c + l2 * z2 ** 2) -
              (m1 + m2) * g * np.sin(theta1)) / l1 / (m1 + m2 * s ** 2)
    z2_dot = ((m1 + m2) * (l1 * z1 ** 2 * s - g * np.sin(theta2) + g * np.sin(theta1) * c) +
              m2 * l2 * z2 ** 2 * s * c) / l2 / (m1 + m2 * s ** 2)

    return theta1_dot, z1_dot, theta2_dot, z2_dot


def simulate(y0, t_max, dt, l1, l2, m1, m2):
    t_eval = np.arange(0, t_max, dt)
    solution = solve_ivp(equations, [0, t_max], y0, t_eval=t_eval, method='RK45', args=(l1, l2, m1, m2))
    return solution.t, solution.y


def draw_pendulum(screen, theta1, theta2, l1, l2, width, height, trace):
    x1 = l1 * np.sin(theta1)
    y1 = l1 * np.cos(theta1)
    x2 = x1 + l2 * np.sin(theta2)
    y2 = y1 + l2 * np.cos(theta2)

    origin = (width // 2, height // 2)
    bob1 = (origin[0] + int(x1 * 100), origin[1] + int(y1 * 100))
    bob2 = (origin[0] + int(x2 * 100), origin[1] + int(y2 * 100))

    # Update trace
    trace.append(bob2)
    if len(trace) > 500:
        trace.pop(0)

    # Draw trace
    for point in trace:
        pygame.draw.circle(screen, (0, 255, 0), point, 2)

    pygame.draw.line(screen, (255, 255, 255), origin, bob1, 2)
    pygame.draw.line(screen, (255, 255, 255), bob1, bob2, 2)
    pygame.draw.circle(screen, (255, 0, 0), bob1, 10)
    pygame.draw.circle(screen, (0, 0, 255), bob2, 10)


def get_user_input(screen, prompt, x, y):
    font = pygame.font.Font(None, 36)
    input_box = pygame.Rect(x, y, 140, 32)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((0, 0, 0))
        txt_surface = font.render(prompt + text, True, color)
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()
        pygame.time.Clock().tick(30)

    return text


def main_menu():
    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))

    theta1 = float(get_user_input(screen, 'Początkowe nachylenie wahadła 1 (°): ', 50, 50))
    theta2 = float(get_user_input(screen, 'Początkowe nachylenie wahadła 2 (°): ', 50, 100))
    z1 = float(get_user_input(screen, 'Początkowa prędkość kątowa wahadła 1 (°/s): ', 50, 150))
    z2 = float(get_user_input(screen, 'Początkowa prędkość kątowa wahadła 2 (°/s): ', 50, 200))
    l1 = float(get_user_input(screen, 'Długość wahadła 1 (m): ', 50, 250))
    l2 = float(get_user_input(screen, 'Długość wahadła 2 (m): ', 50, 300))
    m1 = float(get_user_input(screen, 'Masa wahadła 1 (kg): ', 50, 350))
    m2 = float(get_user_input(screen, 'Masa wahadła 2 (kg): ', 50, 400))

    theta1 = np.radians(theta1)
    theta2 = np.radians(theta2)
    z1 = np.radians(z1)
    z2 = np.radians(z2)

    screen.fill((0, 0, 0))
    draw_pendulum(screen, theta1, theta2, l1, l2, width, height, [])
    font = pygame.font.Font(None, 36)
    preview_text = font.render("Kliknij Enter, aby zacząć symulacje", True, (255, 255, 255))
    screen.blit(preview_text, (width // 2 - preview_text.get_width() // 2, height - 50))
    pygame.display.flip()

    wait_for_enter = True
    while wait_for_enter:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    wait_for_enter = False

    pygame.quit()

    return theta1, theta2, z1, z2, l1, l2, m1, m2


def main():
    theta1, theta2, z1, z2, l1, l2, m1, m2 = main_menu()

    pygame.init()
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    y0 = [theta1, z1, theta2, z2]

    t_max = 20
    dt = 0.01

    t_vals, sol = simulate(y0, t_max, dt, l1, l2, m1, m2)

    running = True
    i = 0
    trace = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0))

        if i < len(t_vals):
            theta1, theta2 = sol[0][i], sol[2][i]
            draw_pendulum(screen, theta1, theta2, l1, l2, width, height, trace)
            i += 1
        else:
            i = 0

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
