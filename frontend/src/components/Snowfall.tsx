import { useEffect, useState } from 'react';

interface Snowflake {
    id: number;
    x: number;
    delay: number;
    duration: number;
    size: number;
    opacity: number;
}

export default function Snowfall() {
    const [snowflakes, setSnowflakes] = useState<Snowflake[]>([]);

    useEffect(() => {
        // Generate snowflakes
        const flakes: Snowflake[] = [];
        for (let i = 0; i < 50; i++) {
            flakes.push({
                id: i,
                x: Math.random() * 100,
                delay: Math.random() * 10,
                duration: 5 + Math.random() * 10,
                size: 3 + Math.random() * 5,
                opacity: 0.3 + Math.random() * 0.5
            });
        }
        setSnowflakes(flakes);
    }, []);

    return (
        <div className="snowfall-container">
            {snowflakes.map(flake => (
                <div
                    key={flake.id}
                    className="snowflake"
                    style={{
                        left: `${flake.x}%`,
                        width: flake.size,
                        height: flake.size,
                        opacity: flake.opacity,
                        animationDelay: `${flake.delay}s`,
                        animationDuration: `${flake.duration}s`
                    }}
                />
            ))}
            <style>{`
                .snowfall-container {
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    pointer-events: none !important;
                    z-index: 9;
                    overflow: hidden;
                }
                
                .snowflake {
                    position: absolute;
                    top: -10px;
                    background: white;
                    border-radius: 50%;
                    animation: snowfall linear infinite;
                    box-shadow: 0 0 4px rgba(255, 255, 255, 0.8);
                    pointer-events: none !important;
                }
                
                @keyframes snowfall {
                    0% {
                        transform: translateY(-10px) rotate(0deg);
                    }
                    100% {
                        transform: translateY(100vh) rotate(360deg);
                    }
                }
            `}</style>
        </div>
    );
}
