import React from 'react';
import { motion } from 'framer-motion';
import { 
  Heart, 
  Linkedin, 
  Github, 
  ExternalLink, 
  Mail,
  Zap,
  Brain,
  Mic,
  Eye
} from 'lucide-react';

interface FooterProps {
  theme: 'light' | 'dark';
}

const Footer: React.FC<FooterProps> = ({ theme }) => {
  const capabilities = [
    {
      icon: Zap,
      title: "LangGraph Orchestration",
      description: "Intelligent agent routing with conditional workflows and quality control loops"
    },
    {
      icon: Brain,
      title: "Multi-Modal Intelligence",
      description: "Process text, images, audio, and documents with specialized AI agents"
    },
    {
      icon: Eye,
      title: "Vision & Voice",
      description: "Advanced image analysis with LLaVA and offline speech processing"
    }
  ];

  const skills = [
    "Python", "LangGraph", "LangChain", "FastAPI", "React", "TypeScript",
    "Ollama", "Mistral", "ChromaDB", "Computer Vision", "NLP", "Multi-Agent Systems"
  ];

  const experiences = [
    {
      title: "B.Tech CSE (AI & ML)",
      organization: "GL Bajaj Group of Institutions",
      type: "education"
    },
    {
      title: "Summer Intern",
      organization: "Celebal Technologies (Data Science)",
      type: "experience"
    },
    {
      title: "SDE Intern",
      organization: "Credora (Full-stack & ML Solutions)",
      type: "experience"
    },
    {
      title: "Data Science Intern",
      organization: "Extion Infotech (96% Model Accuracy)",
      type: "experience"
    }
  ];

  const projectFeatures = [
    "LangGraph Multi-Agent System",
    "Voice Input & Output Processing",
    "Real-time Agent Progress Tracking",
    "Local AI with Mistral & LLaVA",
    "Multi-Modal File Processing",
    "Vector Database Integration"
  ];

  const socialLinks = [
    {
      icon: Linkedin,
      label: "LinkedIn Profile",
      href: "#"
    },
    {
      icon: Github,
      label: "GitHub Repository",
      href: "#"
    },
    {
      icon: ExternalLink,
      label: "Portfolio Website",
      href: "#"
    },
    {
      icon: Mail,
      label: "Email Contact",
      href: "mailto:harsh@example.com"
    }
  ];

  return (
    <footer className={`relative mt-20 ${
      theme === 'dark' 
        ? 'footer-gradient border-t border-slate-800/50' 
        : 'bg-gradient-to-br from-slate-50 to-blue-50 border-t border-slate-200'
    }`}>
      <div className="container mx-auto px-4 py-16">
        {/* Platform Capabilities Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <div className="text-center mb-12">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              <span className="bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                Neurofluxion AI
              </span> Capabilities
            </h2>
            <p className={`text-lg ${
              theme === 'dark' ? 'text-slate-300' : 'text-slate-600'
            }`}>
              Orchestrating Intelligence — Across Voice, Vision, and Thought
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {capabilities.map((capability, index) => {
              const Icon = capability.icon;
              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  whileHover={{ y: -5 }}
                  className={`p-6 rounded-2xl backdrop-blur-md border transition-all duration-300 ${
                    theme === 'dark' 
                      ? 'bg-slate-800/30 border-slate-700/50 hover:bg-slate-800/50' 
                      : 'bg-white/70 border-slate-200/50 hover:bg-white/90'
                  }`}
                >
                  <div className={`w-12 h-12 rounded-xl mb-4 flex items-center justify-center ${
                    theme === 'dark' 
                      ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 text-cyan-400' 
                      : 'bg-gradient-to-br from-cyan-500/10 to-purple-500/10 text-cyan-600'
                  }`}>
                    <Icon size={24} />
                  </div>
                  <h3 className={`text-xl font-semibold mb-2 ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    {capability.title}
                  </h3>
                  <p className={`text-sm ${
                    theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                  }`}>
                    {capability.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* About the Developer Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <div className="text-center mb-12">
            <h2 className={`text-3xl md:text-4xl font-bold mb-4 ${
              theme === 'dark' ? 'text-white' : 'text-slate-900'
            }`}>
              About the Developer
            </h2>
            <div className="w-16 h-1 bg-gradient-to-r from-cyan-500 to-purple-500 mx-auto rounded-full" />
          </div>

          <div className="max-w-6xl mx-auto">
            <div className={`rounded-2xl p-8 backdrop-blur-md border ${
              theme === 'dark' 
                ? 'bg-slate-800/30 border-slate-700/50' 
                : 'bg-white/70 border-slate-200/50'
            }`}>
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                {/* Developer Info - Takes 3 columns */}
                <div className="lg:col-span-3">
                  <h3 className={`text-2xl font-bold mb-4 ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Harsh Mishra
                  </h3>
                  <div className="space-y-4">
                    <p className={`text-base leading-relaxed text-justify ${
                      theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                    }`}>
                      AI/ML engineer specializing in multi-agent systems and LangGraph orchestration. 
                      Expert in building production-ready AI solutions using Python, FastAPI, and modern 
                      frameworks like LangChain for intelligent agent coordination.
                    </p>
                    <p className={`text-base leading-relaxed text-justify ${
                      theme === 'dark' ? 'text-slate-300' : 'text-slate-700'
                    }`}>
                      Proven track record in developing sophisticated AI systems with achievements including 
                      NASA Space Apps Challenge 2024 finalist and TOP 5 ranking at ML Spark Competition. 
                      Passionate about creating intelligent systems that orchestrate multiple AI capabilities.
                    </p>
                  </div>

                  {/* Technical Expertise */}
                  <div className="mt-6">
                    <h4 className={`text-lg font-semibold mb-3 ${
                      theme === 'dark' ? 'text-white' : 'text-slate-900'
                    }`}>
                      Technical Expertise
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {skills.map((skill, index) => (
                        <span key={index} className="skill-tag">
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Education & Experience - Takes 2 columns */}
                <div className="lg:col-span-2">
                  <h4 className={`text-lg font-semibold mb-4 ${
                    theme === 'dark' ? 'text-white' : 'text-slate-900'
                  }`}>
                    Education & Experience
                  </h4>
                  <div className="space-y-4">
                    {experiences.map((exp, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.5, delay: index * 0.1 }}
                        viewport={{ once: true }}
                        className="flex items-start space-x-3"
                      >
                        <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${
                          exp.type === 'education' 
                            ? 'bg-gradient-to-r from-cyan-500 to-blue-500' 
                            : 'bg-gradient-to-r from-purple-500 to-pink-500'
                        }`} />
                        <div className="min-w-0">
                          <h5 className={`font-medium text-sm ${
                            theme === 'dark' ? 'text-white' : 'text-slate-900'
                          }`}>
                            {exp.title}
                          </h5>
                          <p className={`text-xs leading-relaxed ${
                            theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                          }`}>
                            {exp.organization}
                          </p>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Footer Bottom - Centered Layout */}
        <div className="max-w-5xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 pt-8 border-t border-slate-700/30">
            {/* Project Info */}
            <div className="lg:col-start-1">
              <div className="flex items-center space-x-3 mb-4">
                <div className={`p-2 rounded-lg ${
                  theme === 'dark' 
                    ? 'bg-gradient-to-br from-cyan-500/20 to-purple-500/20 text-cyan-400' 
                    : 'bg-gradient-to-br from-cyan-500/10 to-purple-500/10 text-cyan-600'
                }`}>
                  <img 
                    src="/logo.jpg" 
                    alt="Neurofluxion AI" 
                    className="w-5 h-5 rounded"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      e.currentTarget.nextElementSibling!.style.display = 'block';
                    }}
                  />
                  <Zap size={20} style={{ display: 'none' }} />
                </div>
                <h3 className={`text-lg font-semibold ${
                  theme === 'dark' ? 'text-white' : 'text-slate-900'
                }`}>
                  Neurofluxion AI
                </h3>
              </div>
              <p className={`text-sm mb-4 text-justify ${
                theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
              }`}>
                Advanced multi-agent AI system orchestrating intelligence across voice, vision, and thought 
                with LangGraph coordination and local processing capabilities.
              </p>
            </div>

            {/* Connect with Developer - Centered */}
            <div className="lg:col-start-2 lg:pl-4">
              <h3 className={`text-lg font-semibold mb-4 ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                Connect with Developer
              </h3>
              <div className="space-y-3">
                {socialLinks.map((link, index) => {
                  const Icon = link.icon;
                  return (
                    <motion.a
                      key={index}
                      href={link.href}
                      whileHover={{ x: 5 }}
                      className={`flex items-center space-x-3 text-sm transition-colors duration-200 ${
                        theme === 'dark' 
                          ? 'text-slate-400 hover:text-cyan-400' 
                          : 'text-slate-600 hover:text-cyan-600'
                      }`}
                    >
                      <Icon size={16} />
                      <span>{link.label}</span>
                    </motion.a>
                  );
                })}
              </div>
            </div>

            {/* Project Features - Centered */}
            <div className="lg:col-start-3 lg:pl-4">
              <h3 className={`text-lg font-semibold mb-4 ${
                theme === 'dark' ? 'text-white' : 'text-slate-900'
              }`}>
                Project Features
              </h3>
              <div className="space-y-2">
                {projectFeatures.map((feature, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <div className="w-1.5 h-1.5 bg-gradient-to-r from-cyan-500 to-purple-500 rounded-full" />
                    <span className={`text-sm ${
                      theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
                    }`}>
                      {feature}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className={`mt-8 pt-8 border-t text-center ${
          theme === 'dark' ? 'border-slate-700/30' : 'border-slate-200/30'
        }`}>
          <p className={`text-sm flex items-center justify-center space-x-2 ${
            theme === 'dark' ? 'text-slate-400' : 'text-slate-600'
          }`}>
            <span>© 2024 Built with</span>
            <Heart size={14} className="text-red-500" />
            <span>by Harsh Mishra</span>
          </p>
          <div className={`mt-2 text-xs flex items-center justify-center space-x-4 ${
            theme === 'dark' ? 'text-slate-500' : 'text-slate-500'
          }`}>
            <span>AI/ML Engineering</span>
            <span>•</span>
            <span>Multi-Agent Systems</span>
            <span>•</span>
            <span>LangGraph Orchestration</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;