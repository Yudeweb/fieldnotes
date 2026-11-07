"""Kinematics-only draft content. References and marking guides stay on the server."""
from math import atan, degrees, pi, sqrt

SOURCE_ROOT = '/Users/yusufdenizcelik/Downloads/Material (5)'
SOURCES = {
    'mar03': {'title': 'Kinematics · 3 March', 'file': 'Lessons/20260303_Physics_I_Kinematics.pdf', 'pages': [16, 21, 22, 26, 29, 30, 31, 45]},
    'mar05': {'title': 'Kinematics · 5 March', 'file': 'Lessons/20260305_Physics_I_Kinematics.pdf', 'pages': [2, 12, 26, 29, 33, 36]},
    'apr09': {'title': 'Relative motion · 9 April', 'file': 'Lessons/20260409_Physics_I_Gravitation_Relative_motion.pdf', 'pages': [13, 15, 16, 29]},
}


def field(id, label, answer, unit='', tolerance=0.02):
    return dict(id=id, label=label, answer=answer, unit=unit, tolerance=tolerance)


LESSONS = [
    {
        'id': 'describe', 'title': 'Describe the motion', 'subtitle': 'Position, vectors & reference frames', 'minutes': 6,
        'objective': 'Distinguish a position, a displacement, a velocity and a speed.',
        'body': [
            'Choose an origin, axes and a clock before describing a motion. Position is a vector r(t). Displacement is the change in position, Δr = r(t₂) − r(t₁); it depends on the two endpoints. Distance travelled is the length of the path and can be larger than the magnitude of displacement.',
            'Average velocity is Δr/Δt. Instantaneous velocity is the derivative of position and points tangent to the path. Speed is the magnitude of velocity, so speed is nonnegative even when a velocity component is negative.',
            'Acceleration describes changes in velocity. An object can accelerate while maintaining constant speed if its direction changes. Quantities from different observers must be expressed in the same frame before you compare or combine them.'
        ],
        'formulas': ['v = dr/dt', 'a = dv/dt', 'speed = |v|'],
        'example': 'A walker goes 3 m east, then 4 m north. The path length is 7 m, while the displacement magnitude is √(3² + 4²) = 5 m. These are different measurements of the same journey.',
        'pitfall': 'A negative velocity component tells you direction along an axis. It does not mean a negative speed.',
        'references': [['mar03',16], ['mar03',26]], 'checkpoint': 'cp1'
    },
    {
        'id': 'linear', 'title': 'Build a motion model', 'subtitle': 'Uniform & constant-acceleration motion', 'minutes': 8,
        'objective': 'Choose a valid motion equation and track direction changes.',
        'body': [
            'Uniform motion has constant velocity. For one-dimensional motion, x = x₀ + v₀Δt. The position–time graph is a straight line; its slope is the velocity.',
            'For constant acceleration, integrate once to obtain velocity and twice to obtain position. The constant-acceleration equations are only valid over an interval where that acceleration is constant. State the sign convention before substituting values.',
            'If velocity changes sign within the interval, the particle turns around. To find distance travelled, split the journey at each turning time and add the magnitudes of the segment displacements. The final minus initial position gives signed displacement, not necessarily distance.'
        ],
        'formulas': ['v = v₀ + aΔt', 'x = x₀ + v₀Δt + ½aΔt²', 'v² = v₀² + 2a(x − x₀)'],
        'example': 'For v₀ = 3 m/s and a = −4 m/s², the turning time is 0.75 s. At t = 7 s, velocity is −25 m/s and displacement is −77 m. The outward segment is 1.125 m, so the total path length is 79.25 m.',
        'pitfall': 'Deceleration is not automatically a negative number: the sign depends on the chosen axis and on the velocity.',
        'references': [['mar03',22], ['mar03',30], ['mar03',31]], 'checkpoint': 'cp2'
    },
    {
        'id': 'variable', 'title': 'Let acceleration vary', 'subtitle': 'Derivatives, integrals & initial conditions', 'minutes': 7,
        'objective': 'Move between position, velocity and acceleration without assuming constant acceleration.',
        'body': [
            'When position is known as a function of time, differentiate it to get velocity and differentiate again to get acceleration. Carry the units of each coefficient: terms added to a position must all have units of length.',
            'When acceleration is known, integrate it over time to get the change in velocity. Integrate velocity to get the change in position. Each integration needs an initial value; an indefinite integral alone does not determine a unique motion.',
            'In two or three Cartesian dimensions, differentiate or integrate each component separately. The speed is the magnitude of the resulting velocity vector; do not confuse a component derivative with the derivative of speed.'
        ],
        'formulas': ['v(t) = v(t₀) + ∫ a(t) dt', 'r(t) = r(t₀) + ∫ v(t) dt'],
        'example': 'For x(t) = (2 m/s³)t³ − (3 m/s)t + 1 m, v(t) = (6 m/s³)t² − 3 m/s and a(t) = (12 m/s³)t. At t = 2 s, x = 11 m, v = 21 m/s and a = 24 m/s².',
        'pitfall': 'The familiar ½at² formula cannot use an instantaneous a(t) as if it were constant throughout the interval.',
        'references': [['mar03',21], ['mar03',29]], 'checkpoint': 'cp3'
    },
    {
        'id': 'projectile', 'title': 'Split the projectile', 'subtitle': 'Two components, one shared clock', 'minutes': 9,
        'objective': 'Solve a projectile problem using independent component equations.',
        'body': [
            'Use the point-particle, no-air-resistance model with a constant gravitational acceleration. With x horizontal and y upward, aₓ = 0 and aᵧ = −g. Horizontal velocity remains constant while vertical velocity changes.',
            'Resolve the launch velocity into components: v₀ₓ = v₀ cos θ and v₀ᵧ = v₀ sin θ. The horizontal and vertical equations use the same elapsed time. Find that time from the condition you actually know, such as impact at a given height.',
            'At the highest point, vertical velocity is zero but horizontal velocity generally is not. The same-height range formula requires equal initial and final height; use the component equations when landing occurs at a different height.'
        ],
        'formulas': ['x = x₀ + v₀ₓt', 'y = y₀ + v₀ᵧt − ½gt²', 'vᵧ = v₀ᵧ − gt'],
        'example': 'A horizontal launch from 50 m at 20 m/s has x = 40 m and y = 30.4 m after 2 s when g = 9.8 m/s². Its vertical velocity is −19.6 m/s; its horizontal velocity is still 20 m/s.',
        'pitfall': 'At the top of a projectile trajectory, a = −g ŷ, not zero. Zero vertical velocity is not zero acceleration.',
        'references': [['mar05',26], ['mar05',29], ['mar05',36]], 'checkpoint': 'cp4'
    },
    {
        'id': 'circular', 'title': 'Follow a curved path', 'subtitle': 'Circular motion & radius of curvature', 'minutes': 8,
        'objective': 'Separate changes of speed from changes of direction.',
        'body': [
            'Angular position θ measures rotation in radians. Angular velocity is dθ/dt and angular acceleration is dω/dt. On a circle of fixed radius R, speed is R|ω|, tangential acceleration has component Rα in the positive angular direction, and inward normal acceleration has magnitude v²/R.',
            'Uniform circular motion has constant speed and zero tangential acceleration, but nonzero inward acceleration. Its period is the time for one revolution: T = 2π/|ω|. Frequency is 1/T.',
            'For a general smooth path, use the local radius of curvature ρ: a = (dv/dt) t̂ + (v²/ρ) n̂. The tangent and inward-normal components are perpendicular, so their magnitudes combine by the Pythagorean theorem.'
        ],
        'formulas': ['v = R|ω|', 'aₙ = v²/R', '|a| = √(aₜ² + aₙ²)'],
        'example': 'At a point where v = 4 m/s, R = 2 m and aₜ = 6 m/s², the inward acceleration is 8 m/s² and the total magnitude is 10 m/s².',
        'pitfall': '“Constant speed” does not imply “constant velocity.” Direction changes are enough to produce acceleration.',
        'references': [['mar03',45], ['mar05',2], ['mar05',12]], 'checkpoint': 'cp5'
    },
    {
        'id': 'frames', 'title': 'Change the observer', 'subtitle': 'Position, velocity & acceleration composition', 'minutes': 7,
        'objective': 'Translate a motion between frames without mixing coordinates.',
        'body': [
            'For frames whose axes remain parallel, write r = R + r′, where R locates the moving origin in the original frame. Taking time derivatives gives v = V + v′ and a = A + a′. Express each vector in a common basis.',
            'A passenger walking forward at 2 m/s inside a train moving at 10 m/s has ground-frame velocity 12 m/s in that direction. If the passenger walks backward, the relative velocity changes sign. Vector components matter for motion in different directions.',
            'The simple translational formulas require nonrotating relative axes. Rotating frames need additional kinematic terms, introduced in the optional extension. Here we describe motion only; forces and fictitious-force explanations belong to a later dynamics level.'
        ],
        'formulas': ['r = R + r′', 'v = V + v′', 'a = A + a′'],
        'example': 'A train moves east at 10 m/s. A passenger walks west at 2 m/s relative to the train. With east positive, v = 10 + (−2) = 8 m/s.',
        'pitfall': 'A velocity “relative to the train” and one “relative to the ground” cannot be compared without naming the frame.',
        'references': [['apr09',13], ['apr09',15], ['apr09',16]], 'checkpoint': 'cp6'
    },
    {
        'id': 'coordinates', 'title': 'Extend the coordinates', 'subtitle': 'Polar, cylindrical & rotating-frame notation', 'minutes': 8, 'optional': True,
        'objective': 'Recognize changing basis vectors and know when a source needs review.',
        'body': [
            'This extension is an authored derivation from Cartesian/vector kinematics, not a claim that a dedicated polar/cylindrical lecture was located. The syllabus includes these coordinates, but direct source coverage remains to be reviewed. It is not included in scored readiness for this draft.',
            'In plane polar coordinates, x = r cos θ and y = r sin θ. The radial and angular unit vectors change direction as θ changes. Differentiation gives v = ṙ eᵣ + rθ̇ eθ and a = (r̈ − rθ̇²)eᵣ + (rθ̈ + 2ṙθ̇)eθ. Cylindrical coordinates add z, ż e_z and z̈ e_z.',
            'For a rotating frame, the lecture gives v = V + v′ + ω × r′. Acceleration also includes origin acceleration, angular-acceleration, Coriolis and rotational terms. Vectors must be expressed in a common basis; interpreting the associated forces is outside this level.'
        ],
        'formulas': ['v = ṙ eᵣ + rθ̇ eθ + ż e_z', 'aᵣ = r̈ − rθ̇²', 'aθ = rθ̈ + 2ṙθ̇'],
        'example': 'For a fixed-radius circle with constant θ̇ = ω and fixed z, ṙ = r̈ = θ̈ = 0. The formulas reduce to tangential velocity rω and radial acceleration −rω².',
        'pitfall': 'Differentiating only the scalar coordinates misses the changing directions of the polar basis vectors.',
        'references': [['mar03',16], ['apr09',29]], 'checkpoint': None
    },
]

CHECKPOINTS = {
 'cp1': {'title': 'A journey and its displacement', 'lesson': 'describe', 'provenance': 'Authored practice derived from vector definitions; not an original exam question.',
  'prompt': 'A walker goes 3 m east, then 4 m north, in a total of 5 s. Give the distance travelled, displacement magnitude and average-speed magnitude.',
  'fields': [field('distance','Distance travelled',7,'m'),field('displacement','Displacement magnitude',5,'m'),field('speed','Average speed',1.4,'m/s')],
  'hints': ['Distance follows the path; displacement joins the endpoints.','The endpoint displacement is the hypotenuse of a 3–4 right triangle.'],
  'solution': 'Distance = 3 + 4 = 7 m. Displacement magnitude = √(3² + 4²) = 5 m. Average speed = total distance / time = 7/5 = 1.4 m/s. The average-velocity magnitude would instead be 1 m/s.',
  'misconception': 'Distinguish path length from endpoint displacement and speed from velocity.'},
 'cp2': {'title': 'A particle turns around', 'lesson': 'linear', 'provenance': 'Adapted from Exercise Lesson 1, slide 3; separates distance and displacement explicitly. Draft reference independently calculated.',
  'prompt': 'At t = 0, x₀ = 0 and v₀ = +3 m/s. Constant acceleration is −4 m/s². At t = 7 s find signed velocity, signed displacement and total distance travelled.',
  'fields': [field('velocity','Signed velocity',-25,'m/s'),field('displacement','Signed displacement',-77,'m'),field('distance','Total distance travelled',79.25,'m')],
  'hints': ['Find the time when v₀ + at becomes zero.','The turning time is 0.75 s. Add the outward path length and the return path length.'],
  'solution': 'v = 3 − 4×7 = −25 m/s. Δx = 3×7 − 2×7² = −77 m. The turning point is at 0.75 s and x = 1.125 m. Distance = 1.125 + (1.125 + 77) = 79.25 m.',
  'misconception': 'A signed displacement is not total distance when the particle reverses direction.'},
 'cp3': {'title': 'Differentiate the motion', 'lesson': 'variable', 'provenance': 'Authored practice derived from lecture integration/differentiation; not an imported exam.',
  'prompt': 'x(t) = (2 m/s³)t³ − (3 m/s)t + 1 m. Find position, velocity and acceleration at t = 2 s.',
  'fields': [field('position','Position',11,'m'),field('velocity','Velocity',21,'m/s'),field('acceleration','Acceleration',24,'m/s²')],
  'hints': ['Differentiate the polynomial before substituting t = 2 s.','v = 6t² − 3 and a = 12t, with the coefficient units retained.'],
  'solution': 'x(2) = 16 − 6 + 1 = 11 m. v(2) = 6×4 − 3 = 21 m/s. a(2) = 12×2 = 24 m/s².',
  'misconception': 'A position, a velocity and an acceleration have different derivatives and units.'},
 'cp4': {'title': 'One clock, two components', 'lesson': 'projectile', 'provenance': 'Adapted from April 16 mock MCQ 2, with additional component checks. Use g = 9.8 m/s².',
  'prompt': 'A particle is launched horizontally at 20 m/s from y₀ = 50 m, with x₀ = 0. Neglect drag and use y upward, g = 9.8 m/s². Find x, y and signed vertical velocity at t = 2 s.',
  'fields': [field('x','Horizontal position',40,'m'),field('y','Vertical position',30.4,'m'),field('vy','Vertical velocity',-19.6,'m/s')],
  'hints': ['Horizontal acceleration is zero. Initial vertical velocity is zero.','Use y = 50 − ½gt² and vᵧ = −gt.'],
  'solution': 'x = 20×2 = 40 m. y = 50 − ½×9.8×4 = 30.4 m. vᵧ = −9.8×2 = −19.6 m/s.',
  'misconception': 'The object starts with zero vertical velocity, not zero vertical acceleration.'},
 'cp5': {'title': 'Changing speed and direction', 'lesson': 'circular', 'provenance': 'Authored practice derived from the lecture tangential/normal decomposition.',
  'prompt': 'At one instant a particle follows a circle of radius 2 m at speed 4 m/s. Its tangential acceleration magnitude is 6 m/s². Find normal acceleration magnitude and total acceleration magnitude.',
  'fields': [field('normal','Normal acceleration magnitude',8,'m/s²'),field('total','Total acceleration magnitude',10,'m/s²')],
  'hints': ['Normal acceleration magnitude is v²/R.','Tangential and normal components are perpendicular, so square, add and take the square root.'],
  'solution': 'aₙ = 4²/2 = 8 m/s². |a| = √(6² + 8²) = 10 m/s².',
  'misconception': 'Perpendicular acceleration components do not add as scalar magnitudes.'},
 'cp6': {'title': 'Name the observer', 'lesson': 'frames', 'provenance': 'Authored practice derived from translational frame-composition slides.',
  'prompt': 'With east positive, a train moves at +10 m/s and accelerates at +0.5 m/s². At that instant, a passenger walks at −2 m/s relative to the train and has zero acceleration relative to it. Find ground-frame velocity and acceleration. The train axes do not rotate.',
  'fields': [field('velocity','Ground-frame velocity',8,'m/s'),field('acceleration','Ground-frame acceleration',0.5,'m/s²')],
  'hints': ['Use v = V + v′ for parallel, nonrotating axes.','Acceleration transforms as a = A + a′ in this case.'],
  'solution': 'v = 10 + (−2) = +8 m/s. a = 0.5 + 0 = +0.5 m/s².',
  'misconception': 'A constant velocity relative to the train does not imply zero acceleration relative to the ground.'},
}

BOSS = {
 'title': 'The motion challenge', 'minutes': 25,
 'intro': 'Two tasks combine projectile geometry and circular motion. This is formative practice, not an official exam grade. Draft answer guides await your review.',
 'questions': [
  {'id':'trajectories','title':'01 · Two projectile paths','provenance':'Adapted from imported past-exam Exercise 1A, page 1. Exam date unverified. Wording explicitly specifies launch angles and a nonnegative range difference.',
   'prompt':'In SI units, two no-drag projectile paths are y₁ = −(1 m⁻¹)x² + 5x and y₂ = −(3 m⁻¹)x² + 10x. Both start at the origin with positive horizontal velocity. Use g = 9.8 m/s². Find the difference θ₂ − θ₁ between initial launch angles, the common path point with y > 0, the nonnegative difference in horizontal ranges, and projectile 1’s initial speed. A common path point does not imply simultaneous arrival.',
   'fields':[field('angle','Launch-angle difference',degrees(atan(10)-atan(5)),'°',0.03),field('x','Common point: x',2.5,'m'),field('y','Common point: y',6.25,'m'),field('range','Nonnegative range difference',5/3,'m',0.02),field('speed','Projectile 1 initial speed',sqrt(127.4),'m/s',0.03)],
   'hints':['The launch slope is tan θ. Set the trajectories equal for their common point.','For the speed compare the coefficient of x² with g/(2v₀ₓ²).'],
   'solution':'Launch slopes are 5 and 10: θ₂ − θ₁ = 5.599°. Equating paths gives x(2x − 5) = 0, so the positive-height point is (2.5 m, 6.25 m). Ranges are 5 m and 10/3 m, differing by 5/3 m. From g/(2v₀ₓ²) = 1 m⁻¹, v₀ₓ² = 4.9 m²/s²; with v₀ᵧ = 5v₀ₓ, v₀ = √127.4 = 11.287 m/s.'},
  {'id':'orbit','title':'02 · A circular satellite path','provenance':'Adapted from Exercise Lesson 2, slide 5; speed is an added kinematic subquestion. No gravitational-force calculation is required.',
   'prompt':'A satellite follows a uniform circular path 630 km above Earth. Earth’s diameter is 12,740 km and the orbital period is 98 min. Find its speed and acceleration magnitude using only circular kinematics. Convert all data to SI units.',
   'fields':[field('speed','Orbital speed',2*pi*7000000/5880,'m/s',5),field('acceleration','Acceleration magnitude',4*pi*pi*7000000/(5880**2),'m/s²',0.03)],
   'hints':['Orbital radius is Earth’s radius plus altitude, not altitude alone.','R = 7,000,000 m and T = 5,880 s. Use v = 2πR/T, then a = v²/R.'],
   'solution':'R = 12,740/2 + 630 = 7,000 km = 7.0×10⁶ m and T = 5,880 s. v = 2πR/T ≈ 7,480 m/s. a = v²/R ≈ 7.993 m/s².'}
 ]
}


def public_question(question):
    return {k: v for k, v in question.items() if k not in ('hints', 'solution', 'misconception', 'fields')} | {
        'fields': [{k: v for k, v in f.items() if k not in ('answer','tolerance')} for f in question['fields']]
    }


def public_level():
    return {
        'title':'Kinematics', 'status':'Draft · awaiting your academic review', 'version':'0.1.0',
        'lessons':LESSONS, 'checkpoints':{k:public_question(v) for k,v in CHECKPOINTS.items()},
        'boss': {k:v for k,v in BOSS.items() if k != 'questions'} | {'questions':[public_question(q) for q in BOSS['questions']]},
        'sources':{k:{'title':s['title'],'pages':s['pages']} for k,s in SOURCES.items()},
        'review_notes':[
            'All teaching notes, adaptations and answer guides are drafts; no professor approval is implied.',
            'The boss clarifies initial launch angles and explicitly declares the units of trajectory coefficients.',
            'The imported past-exam year is unresolved (folder 2026; filenames 2025).',
            'Polar/cylindrical coverage is an authored extension pending direct source review; it is not scored.',
            'This is a single-device local level demo. There is no live AI tutor, multilingual generation, handwriting recognition or cohort portal yet.',
            'Numeric fields check the final values in fixed displayed units. They do not assess reasoning, general symbolic equivalence or handwritten work.',
            'Source links are restricted to selected lecture pages. Solution PDFs are not served.',
        ]
    }
