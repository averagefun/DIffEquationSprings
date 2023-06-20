from manim import *
import numpy as np
ANIMATION_DURATION = 12

# START CONDITIONS
S0 = [0] * 20
S0[2] = 0.1 # x3
S0[6] = -0.1

class Springs(Scene):
  def construct(self):
    t = ValueTracker(0)
    num = always_redraw(lambda: DecimalNumber().set_value(
          t.get_value()).to_corner(RIGHT + UP))
    static_circles = []
    start_pos = []
    circles = []
    lines = []
    adjacencies = []
    stiffness = []
    
    labels = []
    def connect_with_spring(circle1, circle2, k):
        if circle1[1] > circle2[1]:
            circle1, circle2 = circle2, circle1
        l = always_redraw(lambda: DashedLine(
            circle1[0].get_center(), circle2[0].get_center(), dash_length=(get_dist(
            circle1[0], circle2[0])/15)))
            
        lines.append(l)
        
        # add adjacencies
        row = [lambda: 0.] * 2 * len(circles)
        
        def cos(): 
            return (circle2[0].get_x() - circle1[0].get_x())/get_dist(circle2[0], circle1[0])
        def sin(): 
            return (circle2[0].get_y() - circle1[0].get_y())/get_dist(circle2[0], circle1[0])
            
        if circle1[1] != -1:
            row[circle1[1]*2] = lambda: -cos()
            row[circle1[1]*2+1] = lambda: -sin()
        if circle2[1] != -1:
            row[circle2[1]*2] = cos
            row[circle2[1]*2+1] = sin
        adjacencies.append(row)
        
        # add stiffness
        
        stiffness.append(k)
        # label
        label = Tex(f'$k_{len(lines)}$', font_size=25)
        label.move_to(l.get_center() + UP/3)
        # labels.append(label)
        
    def add_static_circ(pos):
        c = Circle(radius=0.35, color=WHITE).set_fill(
        color=GRAY, opacity=1).move_to(pos)
        static_circles.append((c, len(static_circles)))
        return c, -1
        
    def get_sol(j):
        global S0
        A = np.array([[col() for col in row] for row in adjacencies])
        S0 = ode_solver(S0, A, stiffness)
        return S0[j]
        
    def add_dynamic_circ(pos):
        c = Circle(radius=0.35, color=WHITE).set_fill(
        color=BLACK, opacity=1).move_to(pos)
        start_pos.append(pos)
        circles.append((c, len(circles)))
        return c, len(circles)-1
        
    top_label = Tex(r"$\frac{k_2}{k_1} = 1$", font_size=50).to_edge(UP)
    c0 = add_static_circ(LEFT*2)
    c1 = add_dynamic_circ(UP *2 + RIGHT)
    c2 = add_dynamic_circ(RIGHT*3)
    c3 = add_dynamic_circ(DOWN*2 + RIGHT*3)
    c31 = add_static_circ(DOWN*3 + RIGHT*1)
    c4 = add_dynamic_circ(DOWN)
    c5 = add_dynamic_circ(DOWN*2 + LEFT*2)
    connect_with_spring(c0, c1, 1)
    connect_with_spring(c1, c2, 1)
    connect_with_spring(c2, c3, 1)
    connect_with_spring(c1, c4, 1)
    connect_with_spring(c2, c4, 1)
    connect_with_spring(c3, c31, 1)
    connect_with_spring(c3, c4, 1)
    connect_with_spring(c31, c5, 1)
    connect_with_spring(c4, c5, 1)
    # center_line1 = Line(start_pos[c1[1]] +
    # DOWN, start_pos[c1[1]] + UP, color=WHITE)
    # lines.append(center_line1)
    # center_line2 = Line(start_pos[c2[1]] +
    # DOWN, start_pos[c2[1]] + UP, color=WHITE)
    # lines.append(center_line2)
    
    max_line_z = max(l.z_index for l in lines)
    
    for circle in static_circles + circles:
        circle[0].set_z_index(max_line_z + 1)
        
    self.play(FadeIn(num))
    self.play(*[Create(c[0]) for c in static_circles + circles], run_time=1)
    self.play(*[Create(l) for l in lines], *[FadeIn(l) for l in labels], run_time=1) # + [top_label]
    self.wait()
    # start position animation
    self.play(*[c[0].animate.shift(np.array([S0[c[1]*2], S0[c[1]*2+1], 0.])) for c in circles], run_time=1)
    
    def add_updater(circle):
        circle[0].add_updater(lambda m: circle[0].move_to(
        start_pos[circle[1]] + np.array([get_sol(circle[1]*2), get_sol(circle[1]*2+1), 0.])))
        
    add_updater(c1)
    add_updater(c2)
    add_updater(c3)
    add_updater(c4)
    add_updater(c5)
    self.wait()
    
    # self.play(*[FadeOut(l) for l in labels])
    
    ##################
    # main animation #
    ##################
    self.play(t.animate.set_value(ANIMATION_DURATION),
    run_time=ANIMATION_DURATION, rate_func=linear)
    
def get_dist(o1, o2):
    return ((o1.get_x() - o2.get_x())**2 + (o1.get_y() - o2.get_y())**2)**0.5
    
def ode_solver(S0, A, k):
    nodes = A.shape[1]
    def dSdt(t, S):
        X = S[:nodes]
        V = S[nodes:]
        K = np.zeros((len(k), len(k)), float)
        np.fill_diagonal(K, k)
        R = -np.dot(A.transpose(), np.dot(
        K, np.dot(A, X)))
        return np.concatenate((V, R))
        
    t = np.linspace(0, 0.02, 2)
    return solver(dSdt, y0=S0, t=t, tfirst=True)[-1]
