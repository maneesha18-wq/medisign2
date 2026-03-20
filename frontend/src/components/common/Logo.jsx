import React from 'react';
import { motion } from 'framer-motion';
import { Activity } from 'lucide-react';

/**
 * MediSign Animated Logo Component
 * Provides a consistent, premium branding with medical-themed animations.
 * 
 * @param {string} size - 'small', 'medium', or 'large'
 * @param {boolean} showText - Whether to show the 'MediSign' text
 * @param {string} className - Additional CSS classes
 */
const Logo = ({ size = 'medium', showText = true, className = '' }) => {
    // Size configurations
    const sizes = {
        small: {
            container: 'space-x-2',
            box: 'h-8 w-8 rounded-lg',
            text: 'text-lg',
            icon: 'h-3 w-3',
            ms: 'text-sm'
        },
        medium: {
            container: 'space-x-3',
            box: 'h-10 w-10 rounded-xl',
            text: 'text-xl',
            icon: 'h-4 w-4',
            ms: 'text-lg'
        },
        large: {
            container: 'space-x-4',
            box: 'h-16 w-16 rounded-2xl',
            text: 'text-4xl',
            icon: 'h-6 w-6',
            ms: 'text-2xl'
        }
    };

    const config = sizes[size] || sizes.medium;

    // Animation Variants
    const boxVariants = {
        initial: { scale: 1 },
        animate: {
            scale: [1, 1.03, 1],
            transition: {
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
            }
        },
        hover: {
            scale: 1.1,
            rotate: 2,
            transition: { type: "spring", stiffness: 400, damping: 12 }
        }
    };

    const floatingVariant = {
        animate: {
            y: [0, -4, 0],
            transition: {
                duration: 4,
                repeat: Infinity,
                ease: "easeInOut"
            }
        }
    };

    const staggerContainer = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.08,
                delayChildren: 0.2
            }
        }
    };

    const letterVariant = {
        hidden: { opacity: 0, y: 10, filter: 'blur(4px)' },
        visible: {
            opacity: 1,
            y: 0,
            filter: 'blur(0px)',
            transition: { type: "spring", stiffness: 200, damping: 20 }
        }
    };

    return (
        <motion.div 
            className={`flex items-center ${config.container} ${className}`}
            variants={floatingVariant}
            animate="animate"
        >
            {/* Logo Icon Box */}
            <motion.div
                variants={boxVariants}
                initial="initial"
                animate="animate"
                whileHover="hover"
                className={`${config.box} bg-gradient-to-br from-medical-600 to-medical-500 flex flex-col items-center justify-center text-white shadow-xl shadow-medical-500/10 relative overflow-hidden group`}
            >
                {/* Glossy overlay */}
                <div className="absolute inset-0 bg-gradient-to-tr from-transparent via-white/10 to-transparent transform -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                
                <span className={`${config.ms} font-black italic tracking-tighter drop-shadow-md z-10`}>MS</span>
                
                {/* Pulsing indicator */}
                <motion.div
                    animate={{
                        opacity: [0.3, 0.8, 0.3],
                        scale: [0.8, 1.2, 0.8]
                    }}
                    transition={{
                        duration: 2,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute bottom-1 w-1.5 h-1.5 bg-emerald-400 rounded-full shadow-[0_0_8px_rgba(52,211,153,0.5)]"
                />
            </motion.div>

            {/* MediSign Text */}
            {showText && (
                <motion.div
                    variants={staggerContainer}
                    initial="hidden"
                    animate="visible"
                    className={`${config.text} font-black text-slate-900 dark:text-white tracking-tighter flex`}
                >
                    {"MediSign".split("").map((char, index) => (
                        <motion.span
                            key={index}
                            variants={letterVariant}
                            className={char === "S" ? "text-medical-600 drop-shadow-sm" : ""}
                        >
                            {char}
                        </motion.span>
                    ))}
                </motion.div>
            )}
        </motion.div>
    );
};

export default Logo;
