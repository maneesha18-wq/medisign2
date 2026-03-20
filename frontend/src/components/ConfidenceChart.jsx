import React from 'react';
import { motion } from 'framer-motion';

/**
 * ConfidenceChart — displays all predicted class probabilities as
 * animated horizontal bars, sorted highest-to-lowest.
 *
 * Props:
 *   predictions  : { [label: string]: number }  — all_predictions from the API
 *   topLabel     : string                        — the predicted (top-1) label
 *   maxRows      : number (default: 10)          — max bars to show
 */
const ConfidenceChart = ({ predictions = {}, topLabel = '', maxRows = 10 }) => {
    if (!predictions || Object.keys(predictions).length === 0) return null;

    const sorted = Object.entries(predictions)
        .sort(([, a], [, b]) => b - a)
        .slice(0, maxRows);

    // Colour palette — top-1 gets the accent colour, rest get slate
    const barColour = (label, rank) => {
        if (label === topLabel) return 'bg-medical-500 dark:bg-medical-400';
        if (rank === 1) return 'bg-slate-400 dark:bg-slate-500';
        return 'bg-slate-200 dark:bg-slate-700';
    };

    const textColour = (label) =>
        label === topLabel
            ? 'text-medical-700 dark:text-medical-300 font-black'
            : 'text-slate-600 dark:text-slate-400 font-medium';

    return (
        <div className="space-y-2.5">
            <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-3">
                Full Probability Map  ({sorted.length} classes)
            </p>
            {sorted.map(([label, prob], idx) => {
                const pct = (prob * 100).toFixed(1);
                const isTop = label === topLabel;
                return (
                    <motion.div
                        key={label}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.04 }}
                        className={`rounded-xl p-2.5 transition-colors ${
                            isTop
                                ? 'bg-medical-50/60 dark:bg-medical-500/10 ring-1 ring-medical-200 dark:ring-medical-800/40'
                                : ''
                        }`}
                    >
                        <div className="flex items-center justify-between mb-1.5">
                            <span className={`text-xs leading-none truncate max-w-[65%] ${textColour(label)}`}>
                                {isTop && (
                                    <span className="inline-block w-1.5 h-1.5 rounded-full bg-medical-500 mr-1.5 mb-0.5 align-middle" />
                                )}
                                {label}
                            </span>
                            <span className={`text-[11px] tabular-nums leading-none ${
                                isTop
                                    ? 'text-medical-600 dark:text-medical-400 font-black'
                                    : 'text-slate-400 dark:text-slate-500 font-semibold'
                            }`}>
                                {pct}%
                            </span>
                        </div>

                        <div className="w-full h-2 bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                            <motion.div
                                initial={{ width: 0 }}
                                animate={{ width: `${pct}%` }}
                                transition={{ duration: 0.7, ease: 'easeOut', delay: idx * 0.04 }}
                                className={`h-full rounded-full ${barColour(label, idx)}`}
                            />
                        </div>
                    </motion.div>
                );
            })}
        </div>
    );
};

export default ConfidenceChart;
