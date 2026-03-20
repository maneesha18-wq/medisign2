import React from 'react';
import { motion, useMotionValue, useTransform, useSpring } from 'framer-motion';
import Logo from '../components/common/Logo';

const AuthLayout = ({ children, title, subtitle }) => {
    // 3D Motion Values for Tilt Effect
    const mouseX = useMotionValue(0);
    const mouseY = useMotionValue(0);

    // Transforms for smooth 3D rotation
    const rotateX = useSpring(useTransform(mouseY, [-0.5, 0.5], [10, -10]), { stiffness: 300, damping: 30 });
    const rotateY = useSpring(useTransform(mouseX, [-0.5, 0.5], [-10, 10]), { stiffness: 300, damping: 30 });

    const handleMouseMove = (e) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const width = rect.width;
        const height = rect.height;
        const mouseXRelative = (e.clientX - rect.left) / width - 0.5;
        const mouseYRelative = (e.clientY - rect.top) / height - 0.5;
        mouseX.set(mouseXRelative);
        mouseY.set(mouseYRelative);
    };

    const handleMouseLeave = () => {
        mouseX.set(0);
        mouseY.set(0);
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-950 px-4 py-12 sm:px-6 lg:px-8 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-medical-100 dark:from-medical-900/20 via-slate-50 dark:via-slate-950 to-medical-50 dark:to-medical-900/10 transition-colors duration-500 overflow-hidden relative perspective-1000">
            {/* Background Decorative Elements */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                {[...Array(6)].map((_, i) => (
                    <motion.div
                        key={i}
                        className="absolute rounded-full bg-medical-500/5 dark:bg-medical-400/5 blur-3xl"
                        initial={{
                            x: Math.random() * 100 - 50 + "%",
                            y: Math.random() * 100 - 50 + "%",
                            scale: Math.random() * 0.5 + 0.5
                        }}
                        animate={{
                            x: [
                                Math.random() * 100 - 50 + "%",
                                Math.random() * 100 - 50 + "%",
                                Math.random() * 100 - 50 + "%"
                            ],
                            y: [
                                Math.random() * 100 - 50 + "%",
                                Math.random() * 100 - 50 + "%",
                                Math.random() * 100 - 50 + "%"
                            ]
                        }}
                        transition={{
                            duration: 20 + Math.random() * 10,
                            repeat: Infinity,
                            ease: "linear"
                        }}
                        style={{
                            width: 300 + Math.random() * 300,
                            height: 300 + Math.random() * 300,
                        }}
                    />
                ))}
            </div>

            <motion.div
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
                initial={{ opacity: 0, y: 40, scale: 0.9, rotateX: 15, rotateY: -10 }}
                animate={{ opacity: 1, y: 0, scale: 1, rotateX: 0, rotateY: 0 }}
                style={{ rotateX, rotateY, transformStyle: "preserve-3d" }}
                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                className="max-w-md w-full space-y-8 bg-white/80 dark:bg-slate-900/80 backdrop-blur-xl p-8 rounded-[2.5rem] shadow-[0_50px_100px_-20px_rgba(0,0,0,0.15)] dark:shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] border border-white/40 dark:border-slate-800 transition-colors relative z-10"
            >
                <div style={{ transform: "translateZ(50px)" }}>
                    <div className="flex justify-center">
                        <Logo size="large" showText={false} />
                    </div>
                    <h2 className="mt-6 text-center text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-slate-900 via-medical-600 to-slate-900 dark:from-white dark:via-medical-400 dark:to-white tracking-tight">
                        {title}
                    </h2>
                    {subtitle && (
                        <p className="mt-2 text-center text-sm text-slate-600 dark:text-slate-400 font-medium">
                            {subtitle}
                        </p>
                    )}
                </div>
                <div style={{ transform: "translateZ(30px)" }}>
                    {children}
                </div>
            </motion.div>
        </div>
    );
};

export default AuthLayout;
