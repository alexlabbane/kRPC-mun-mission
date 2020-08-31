# Autonomous Rocket Simulation | Python | Kerbal Space Program
This project uses the game Kerbal Space Program as a simulation environment for orbital mechanics. A Python script was written that takes a rocket from the surface of the Earth to the surface of the Moon with no human intervention. Although two-body approximations are used, the math is similar to that which allowed the Apollo missions to land on the moon (they used two-body approximations as well), so it allowed me to learn a lot about orbital mechanics.

# Click image below for video demo
[![Youtube Video](http://img.youtube.com/vi/G5khlqxXUh8/0.jpg)](http://www.youtube.com/watch?v=G5khlqxXUh8 "Video Demo")

# Challenge
Write a script to automatically pilot a rocket to the surface of the moon in Kerbal Space Program with no human intervention required.

# Solution
The kRPC mod was used to gain access to an API that can send and receive data to the rocket. A wide variety of languages are supported, but Python was chosen because of its quick prototyping ability. A variety of scripts were also written to experimentally determine specific constants for various engines (i.e. thrust as a function of atmospheric pressure, mass burn rate as a function of thrust, etc.)

## Getting to Orbit
The first step in any mission is to orbit the Earth (called Kerbin in the game). To achieve this, a "gravity" turn is simulated by the script. After liftoff, it slowly pitches over as it climbs in altitude until it is completely horizontal when its apoapsis (the highest point of its orbit) reaches 70km. Then, it waits until it approaches this high point and burns prograde (tangent to its flight path) to accelerate and circularize its orbit.

## Leaving Orbit
A Hohmann Transfer is used to leave orbit of the Earth and enter the Moon's sphere of influence. Given the orbital parameters of the rocket and the position of the moon, the transfer equation is solved, and the script waits until the proper time to execute the burn. To learn more about what a Hohmann Transfer is and how it works, see https://en.wikipedia.org/wiki/Hohmann_transfer_orbit.

## Landing
Once in the Moon's sphere of influence, the rocket decelerates into a free-fall towards the surface. From here, it begins constantly running calculations to determine when it should start the landing burn. For the sake of a challenge, I decided to implement a "suicide burn" in this project. That means the rocket will wait until the last possible second to start the landing burn and then go full throttle all the way until landing. If calculated correctly, this saves fuel, but it leaves very little margin for error.

I derived the velocity and position functions of the vessel from the acceleration. This ended up being much more complex than the basic kinematic equations you may remember from physics because as the vessel burns fuel, its mass changes as a function of time. Thus, the final equations ended up being quite complex but produce very consistent results.

# Conclusion
Overall, this project was a huge success and was very fun to work on. I was able to practice my Python skills, apply my physics knowledge to what felt like a real-world problem, and I picked up a lot of knowledge of orbital mechanics as well.
