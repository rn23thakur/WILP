Take a **Message Signal** (the music/data) and use it to vary the **Frequency** of a **Carrier Wave** (the radio signal).
#### 1. The Building Blocks

Let's define our two signals:

- The Carrier ($c(t)$): A high-frequency radio wave.$$c(t) = A_c \cos(2\pi f_c t)$$
    - $A_c$: Amplitude (Constant).
    - $f_c$: Carrier Frequency (Constant).

- **The Message ($m(t)$):** The low-frequency data we want to send (e.g., your voice).
#### 2. The Core Definition

In FM, the Instantaneous Frequency ($f_i$) of the carrier changes based on the message:

$$f_i(t) = f_c + k_f m(t)$$

- $k_f$: The **frequency sensitivity** constant (how "sensitive" the oscillator is to the voltage of the message).
#### 3. The Integration Problem (The Crucial Step)

A standard wave equation looks like this: $A \cos(\theta(t))$.

We usually write $\theta(t) = 2\pi f t$. But we can't do that here because $f$ is changing!

In calculus, frequency is defined as the rate of change of phase (angle):
$$f = \frac{1}{2\pi} \frac{d\theta}{dt}$$
To find the phase angle $\theta(t)$ to put inside our cosine function, we must do the reverse—we must integrate the frequency:
$$\theta(t) = 2\pi \int_{0}^{t} f_i(\tau) d\tau$$
Substitute our definition from step 2 ($f_i(t) = f_c + k_f m(t)$):
$$\theta(t) = 2\pi \int_{0}^{t} (f_c + k_f m(\tau)) d\tau$$
Solving the integral:
$$\theta(t) = 2\pi f_c t + 2\pi k_f \int_{0}^{t} m(\tau) d\tau$$
#### 4. The Final FM Equation

Now we plug that phase $\theta(t)$ back into the cosine function.

This is the general equation for an FM signal:
$$s_{FM}(t) = A_c \cos\left( 2\pi f_c t + 2\pi k_f \int_{0}^{t} m(\tau) d\tau \right)$$

#### 5. How do we get the data back? (Demodulation)

Since we used **Integration** (summing up changes) to encode the message into the phase, we use the exact reverse operation to get it back: **Differentiation** (measuring the rate of change).

##### The Math of Retrieval

Recall our FM signal equation (where $\theta(t)$ is the total phase):
$$s(t) = A_c \cos(\theta(t))$$

If we run this signal through a circuit called a **Differentiator** (which physically takes the derivative $\frac{d}{dt}$), look what happens to the math:

$$y(t) = \frac{d}{dt} \left[ A_c \cos(\theta(t)) \right]$$

Using the Chain Rule ($\frac{d}{dt}\cos(u) = -\sin(u) \cdot u'$):
$$y(t) = -A_c \sin(\theta(t)) \cdot \underbrace{\frac{d\theta}{dt}}_{\text{This is Frequency!}}$$

Notice that term at the end: $\frac{d\theta}{dt}$.

From our earlier definition, we know that frequency is the derivative of phase: $\frac{d\theta}{dt} = 2\pi(f_c + k_f m(t))$.

So, the output becomes:

$$y(t) = -A_c \underbrace{[2\pi(f_c + k_f m(t))]}_{\text{Amplitude}} \sin(\theta(t))$$

Suddenly, your message $m(t)$, which was hidden inside the frequency, has "popped out" and is now multiplying the amplitude. We can now use a simple **Envelope Detector** (like in AM radio) to peel off that outer amplitude layer and recover your voice.

### A Concrete Example (Single Tone FM)

Let's make this easier to visualize. Assume our message is a simple pure tone (sine wave):
$$m(t) = A_m \cos(2\pi f_m t)$$

1. Integrate the message:
    $$\int A_m \cos(2\pi f_m t) dt = \frac{A_m}{2\pi f_m} \sin(2\pi f_m t)$$
    
2. Substitute into the main equation:
    $$s_{FM}(t) = A_c \cos\left( 2\pi f_c t + 2\pi k_f \left( \frac{A_m}{2\pi f_m} \sin(2\pi f_m t) \right) \right)$$
    
3. Simplify using the Modulation Index ($\beta$):
    
    We group the constants into a single term called $\beta$ (Beta).
    $$\beta = \frac{k_f A_m}{f_m} = \frac{\Delta f}{f_m}$$
    
    - $\Delta f$: Peak frequency deviation (how far the pitch wiggles from the center).
    - $f_m$: How fast the pitch wiggles.
    
    The Final "Single Tone" FM Equation:
    $$s_{FM}(t) = A_c \cos( 2\pi f_c t + \beta \sin(2\pi f_m t) )$$
**Notice the weirdness:** We have a sine wave _inside_ a cosine function! This creates a complex set of sidebands (infinite harmonics), which is why FM sounds clearer than AM but requires more bandwidth.

#### The "Sine inside Cosine" (Infinite Sidebands)
$$s(t) = A_c \cos(2\pi f_c t + \beta \sin(2\pi f_m t))$$
(Note: $\beta$ is the "Modulation Index"—it represents how much the carrier frequency is being pushed around).

This looks like $\cos(A + B)$. We can use the trig identity $\cos(A+B) = \cos A \cos B - \sin A \sin B$:
$$s(t) = A_c [\cos(2\pi f_c t)\cos(\beta \sin(2\pi f_m t)) - \sin(2\pi f_c t)\sin(\beta \sin(2\pi f_m t))]$$
term like $\cos(\beta \sin(\dots))$. This is a periodic function of a periodic function. We have to expand it using **Bessel Functions ($J_n$)**.$$\cos(\beta \sin x) = J_0(\beta) + 2J_2(\beta)\cos(2x) + 2J_4(\beta)\cos(4x) + \dots$$
$$\sin(\beta \sin x) = 2J_1(\beta)\sin(x) + 2J_3(\beta)\sin(3x) + \dots$$

Result:
When you plug these infinite series back into the original equation, you don't just get the carrier frequency $f_c$. You get:

- $f_c$ (The Carrier)
- $f_c \pm f_m$ (First sidebands)
- $f_c \pm 2f_m$ (Second sidebands)
- $f_c \pm 3f_m$ (Third sidebands)
- ...and so on, forever.
mathematically creating "echoes" of the carrier at every multiple of the message frequency. This is why FM theoretically has **infinite bandwidth**.

#### What is bandwidth

Bandwidth is simply the **width of the "real estate"** your signal occupies on the radio spectrum.
**Visualizing it:** Imagine the radio spectrum is a highway.
- **AM Radio** is a motorcycle. It is narrow. It only needs $f_c \pm f_m$
- **FM Radio** is a wide-load truck. Because of those infinite sidebands (the Bessel expansion), it spills over onto the shoulders of the road.
Wait, if it's infinite, how do we use it?
Luckily, the Bessel functions $J_n(\beta)$ get closer to zero as $n$ increases. Eventually, the sidebands become so tiny they don't matter.
We use a "rule of thumb" called **Carson's Rule** to decide how wide the truck actually is for practical purposes (containing ~98% of the energy):
$$B_{FM} \approx 2(\Delta f + f_m)$$

- $\Delta f$: Peak deviation (how far the frequency swings).
- $f_m$: Highest frequency in your message (your voice pitch).

We pay for quality with spectral efficiency, because spreading the signal out makes it incredibly resistant to noise.

#### Notes for self
Mathematically, there is **nothing wrong** with writing $\cos(\beta \sin(2\pi f_m t))$. It is a perfectly valid function. The problem is **engineering utility.** We "can't deal with it" in that form because **it hides the information we actually care about: The Frequency Spectrum.**
The frequency domain expansion (bessel functions) actually help us break this periodic inside periodic into it's ingredients.

**Why does this matter?** In radio, the government (like the FCC) "rents" you a specific slice of the airwaves (say, 100.1 MHz to 100.3 MHz). They strictly enforce this. If you just look at the equation $s(t) = \cos(2\pi f_c t + \sin(\dots))$, you cannot look at that algebra and instantly answer: **"Does this signal fit inside my rented slice, or will it spill over and jam the police radio next door?"**

Radio receivers are built using Filters.

A filter is a gate that says, "I will let 100 MHz pass, but I will block 105 MHz."
Electronic circuits (capacitors and inductors) react to **pure sine waves**.

- They know how to block $\sin(2\pi \cdot 100t)$.
- They know how to pass $\sin(2\pi \cdot 200t)$.
- They **do not** have a rule for how to handle a complex blob like $\cos(\sin(t))$.

To design a circuit that processes this signal, we must know what pure sine waves it is made of. The expansion tells us: "This complex blob is actually just a sum of a 100 MHz sine, a 101 MHz sine, and a 99 MHz sine."

Once we know that, we can build a filter for those three specific numbers.

### The Fourier Connection

You know that for **any** periodic signal $f(t)$, we can calculate its component frequencies (coefficients) using the Fourier integral:

$$\text{Coefficient}_n = \frac{1}{T} \int_{0}^{T} f(t) \cdot e^{-j n \omega t} dt$$

Now, let's play "Plug and Chug."

Let our signal be the complex FM wave: $f(t) = e^{j \beta \sin(\omega t)}$.

If you try to find the Fourier Coefficient ($C_n$) for the $n$-th harmonic of this FM wave, you have to solve this integral:

$$C_n = \frac{1}{2\pi} \int_{-\pi}^{\pi} e^{j(\beta \sin(\theta) - n\theta)} d\theta$$
If you look up the **definition of a Bessel Function ($J_n(\beta)$)** in a pure math textbook (completely unrelated to radio), you will find this:

$$J_n(\beta) = \frac{1}{2\pi} \int_{-\pi}^{\pi} e^{j(\beta \sin(\theta) - n\theta)} d\theta$$
- **Fourier Series** is the **General Tool**: It tells you "To find the harmonics of ANY wave, solve this integral."
- **Bessel Functions** are the **Specific Solution**: It tells you "When that wave happens to be a sine-inside-a-cosine (FM), the solution to the Fourier integral is called $J_n$."