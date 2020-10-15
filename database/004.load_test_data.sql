-- UTF-8 without BOM
-- скрипт выполняется от имени пользователя qi_user
-- скрипт загружает тестовые данные в таблицы базы данных

SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET search_path TO qi;

DELETE FROM workflow_monthly_jobs;

COPY qi.workflow_monthly_jobs (wmj_id, wmj_active, wmj_quantity, wmj_eft, wmj_remarks) FROM stdin;
1	t	10	[Nidhoggur, pillow wang's Nidhoggur]\nImperial Navy Drone Damage Amplifier\nImperial Navy Drone Damage Amplifier\nImperial Navy Drone Damage Amplifier\nOmnidirectional Tracking Enhancer II\nSentient Drone Damage Amplifier\n\n500MN Microwarpdrive II\nDrone Navigation Computer I\nDrone Navigation Computer I\nSentient Omnidirectional Tracking Link,Optimal Range Script\nSentient Omnidirectional Tracking Link,Optimal Range Script\nSentient Sensor Booster,Scan Resolution Script\n\nFighter Support Unit II\nFighter Support Unit II\nFighter Support Unit II\nFighter Support Unit II\nFighter Support Unit II\n\nCapital Core Defense Field Extender I\nCapital Core Defense Field Extender I\nCapital Core Defense Field Extender I	https://zkillboard.com/kill/80881687/
2	t	60	[Stratios, Vinnegar Douche's Stratios]\nDamage Control II\nDrone Damage Amplifier II\nMultispectrum Energized Membrane II\nTrue Sansha Medium Armor Repairer\nTrue Sansha Medium Armor Repairer\n\n10MN Afterburner II\nCaldari Navy Warp Scrambler\nRepublic Fleet Large Cap Battery\nRepublic Fleet Large Cap Battery\nStasis Webifier II\n\nCovert Ops Cloaking Device II\nMedium Gremlin Compact Energy Neutralizer\nSmall Energy Neutralizer II\nSmall Energy Neutralizer II\nSisters Core Probe Launcher,Sisters Core Scanner Probe\n\nMedium Auxiliary Nano Pump II\nMedium Capacitor Control Circuit II\nMedium Explosive Armor Reinforcer I\n\nFederation Navy Hobgoblin x10\nFederation Navy Ogre x4\nFederation Navy Hammerhead x10\nWarrior II x10	funny kill: https://zkillboard.com/kill/83778181/\nwith a history: https://www.youtube.com/watch?v=UYFOtdujO5s
3	t	1	[Iteron Mark V, Kemul's Iteron Mark V]\n\n\n\n\n\n\n\nXray S\nCorpum C-Type EM Energized Membrane x3\nDread Guristas Silver Tag x2\nMotley Compound\nVespa I Blueprint (Copy) x2\nProjectile Weapon Rigging\nMexallon x20807\nWarrior I Blueprint\nConductive Polymer\nSalvager I\nSalvager I\nDread Guristas Explosive Shield Amplifier\nCaldari Navy Scourge Light Missile x6233\nWarrior I Blueprint (Copy) x2\n'Integrated' Vespa x8\nHigh-Tech Manufacturing Tools x3\nSmashed Trigger Unit x3\nDecayed Medium Cap Battery Mutaplasmid\nMobile Tractor Unit\nMining Foreman Burst I Blueprint (Copy)\nDecayed Assault Damage Control Mutaplasmid x4\nMissile Range Script\nECCM Script\n400mm Crystalline Carbonide Restrained Plates\nCorpii A-Type Small Remote Capacitor Transmitter x4\nLeshak Blueprint (Copy)\nPyerite x53574\nCorpum C-Type Kinetic Energized Membrane\nDrone Tactical Limb x28\nAccelerant Decryptor\nDecayed Warp Scrambler Mutaplasmid\nHammerhead II x10\nDecayed Stasis Webifier Mutaplasmid\nBlood Palladium Tag\nDark Blood Kinetic Energized Membrane x5\nScan Pinpointing Array II\nDark Blood Kinetic Coating\nBlood Silver Tag x3\nZor's Custom Navigation Link x5\nDark Blood Radio S x4\nCorpii A-Type Explosive Coating\nCalm Dark Filament x6\nIsogen x6137\nLarge Shield Extender II x2\nLarge Shield Extender II x4\nDrone Cerebral Fragment x68\nSynth Crash Booster\nMetal Scraps x15\nDatacore - Triglavian Quantum Engineering x2\nMinmatar Encryption Methods x2\nAgency 'Pyrolancea' DB3 Dose I x2\nLucent Compound\nCrosslink Compact Ballistic Control System\nBallistic Control System II x2\nDark Blood Brass Tag x9\nFFR Enduring Assault Damage Control\nDark Blood Microwave S x3\nMjolnir Light Missile x400\nExpanded Probe Launcher I\nDecayed 5MN Microwarpdrive Mutaplasmid\nTritanium x24044\nCalm Electrical Filament x8\nDark Blood Standard S\nCalm Exotic Filament x8\nShield Extension Charge x224\nSynth Exile Booster\nNocxium x382\nHigh-Tech Data Chip x6\nRadiation Absorption Thruster x110\nFierce Dark Filament x14\nInfrared S\nMegacyte x34\nFleeting Compact Stasis Webifier x6\nDecayed Damage Control Mutaplasmid x3\nContaminated Lorentz Fluid x3\nCorpii A-Type Kinetic Coating x3\nCompact Entropic Radiation Sink x2\nAgency 'Hardshell' TB5 Dose II\nInitiated Compact Warp Scrambler\nZero-Point Field Manipulator x153\nTriglavian Survey Database x4197\nDrone Capillary Fluid x1175\n1MN Afterburner II\nBlood Copper Tag\nMelted Capacitor Console x7\nDecayed Heat Sink Mutaplasmid\nBlood Infrared S\nDark Blood Silver Tag x7\nHigh-Tech Scanner x4\nDecayed 500MN Microwarpdrive Mutaplasmid\nBlood Infrared M x2\nDark Blood Thermal Coating x2\nScorched Telemetry Processor\nSisters Combat Scanner Probe x8\nBlood Standard S x3\nDecayed Heavy Energy Neutralizer Mutaplasmid x2\nOptimized Attainment Decryptor\nHeron Blueprint (Copy)\nAgency 'Hardshell' TB3 Dose I x4\nMedium Capacitor Booster II\nPower Circuit\nLattice Locked Dekaisogen x81\nDrone Synaptic Relay Wiring x2188\nBurned Logic Circuit x16\nSmall F-RX Compact Capacitor Booster\nDrone Interfacing\nArmor Plates x9\n8th Tier Overseer's Personal Effects x10\nAgitated Firestorm Filament x6\nFierce Gamma Filament x3\nCharred Micro Circuit x17\nCorpii A-Type EM Coating x3\nMedium Infectious Scoped Energy Neutralizer\nBlood Ultraviolet S\nParity Decryptor x3\nBlood Radio S x9\nDecayed Entropic Radiation Sink Mutaplasmid\nTrinary State Processor x543\nSynth Drop Booster\n5th Tier Overseer's Personal Effects\nCalm Gamma Filament x10\nDecayed Magnetic Field Stabilizer Mutaplasmid x2\nRaging Firestorm Filament x2\nScourge Light Missile x100\nScourge Light Missile x200\nGravid Warp Disruptor Mutaplasmid\nRepublic Fleet 10MN Afterburner\nSmall Murky Compact Remote Shield Booster\nBroken Drone Transceiver x4\nDread Guristas Explosive Shield Hardener\n5MN Quad LiF Restrained Microwarpdrive x2\nUnstable Large Ancillary Shield Booster Mutaplasmid\nInterface Circuit x2\nCapacitor Power Relay II\nCapacitor Power Relay II\nDrone Sharpshooting\nZero-Point Condensate x944\nMalfunctioning Shield Emitter\nDecayed Medium Energy Neutralizer Mutaplasmid\nMining Foreman\nAugmentation Decryptor x2\nDamage Control II\n'Integrated' Acolyte x6\n'Integrated' Acolyte\nDecayed Warp Disruptor Mutaplasmid x2\nGistum C-Type Thermal Shield Amplifier\nFried Interface Circuit x19\nDomination EM Shield Hardener\nSalvager II\nSalvager II x2\nBlood Microwave S x3\nFierce Firestorm Filament x13\nDecayed X-Large Shield Booster Mutaplasmid\nHobgoblin I x2\nAlloyed Tritanium Bar x2\nBlood Microwave M\nDark Blood Copper Tag x18\nTracking Speed Script\nCaldari Navy Hornet x5\nCorpum C-Type Medium Remote Capacitor Transmitter\nRepublic Fleet Large Shield Extender\nHobgoblin II\nHobgoblin II x3\nCorpum C-Type Thermal Energized Membrane\nCrystalline Isogen-10 x256\nContaminated Nanite Compound x8\nGravid X-Large Shield Booster Mutaplasmid\nDecayed Small Shield Extender Mutaplasmid\nSingle-crystal Superalloy I-beam\nDark Blood EM Energized Membrane x2\n1st Tier Overseer's Personal Effects x12\nUnstable Damage Control Mutaplasmid\nDark Blood Explosive Armor Hardener x2\nMid-grade Talisman Alpha\nRogue Drone 46-X Nexus Chip\nAgency 'Pyrolancea' DB5 Dose II x2\nArbalest Compact Light Missile Launcher\nGlossy Compound\nDefective Current Pump x7\nBlood Brass Tag\nHornet I x4\nCaldari Navy Vespa\nCaldari Navy Vespa x4\n1MN Y-S8 Compact Afterburner x2\nPithum C-Type EM Shield Amplifier\nSymmetry Decryptor\nBlood Radio M x4\nEnergy Pulse Weapons\nDark Blood EM Armor Hardener\nZydrine x231\nRelic Analyzer II\nSynth Mindflood Booster\nMid-grade Talisman Beta\n7th Tier Overseer's Personal Effects x22\nTargeting Range Script x2\nTangled Power Conduit x18\nSingularity Radiation Convertor x50\nSensor Booster II\nReactive Armor Hardener\nCore Probe Launcher I\nTripped Power Circuit x25\n\n	funny dump of modules: https://zkillboard.com/kill/82493494/
4	f	1	[Rorqual, Handsome Jack's Rorqual]\nExpanded Cargohold II\nExpanded Cargohold II\nExpanded Cargohold II\nExpanded Cargohold II\n\n50000MN Y-T8 Compact Microwarpdrive\nCONCORD Capital Shield Booster\nGistum C-Type Multispectrum Shield Hardener\nGistum C-Type Multispectrum Shield Hardener\nGistum C-Type Thermal Shield Amplifier\nPithum A-Type EM Shield Amplifier\nCapital Capacitor Booster II,Navy Cap Booster 3200\n\nCONCORD Capital Remote Shield Booster\nCapital Tractor Beam I\nCynosural Field Generator I\nIndustrial Core II\nPulse Activated Nexus Invulnerability Core\nMining Foreman Burst II,Mining Equipment Preservation Charge\nMining Foreman Burst II,Mining Laser Field Enhancement Charge\nMining Foreman Burst II,Mining Laser Optimization Charge\n\nCapital Drone Mining Augmentor I\nCapital Drone Mining Augmentor II\nCapital Drone Mining Augmentor II\n\nValkyrie II x100\nValkyrie II x2\nImperial Navy Curator x11\nImperial Navy Curator x1\nWarrior II x29\n'Excavator' Mining Drone x4\n'Excavator' Mining Drone x1\nVespa II x61\n\nXray S\nMedium Asymmetric Enduring Remote Shield Booster\nBlood Bronze Tag\nSuppressed Targeting System I x12\nMicrowave L x5\nMedium F-RX Compact Capacitor Booster x3\nUpgraded Armor Thermal Hardener I x10\nSmall Focused Anode Particle Stream I\nUpgraded Energized Explosive Membrane I x3\nDenny Enduring Omnidirectional Tracking Link x10\n400mm Crystalline Carbonide Restrained Plates x13\nLarge Inefficient Hull Repair Unit x20\nClutch Restrained Warp Disruption Field Generator x5\nInfiltrator I x33\nDual Heavy Afocal Pulse Maser I x2\nLimited Energized Armor Layering Membrane I\nWasp I x49\nAnode Light Neutron Particle Cannon I\nMedium Compact Pb-Acid Cap Battery x13\nGamma S x3\nAcolyte I x4\nType-D Restrained Capacitor Power Relay x7\nInfrared L x6\nSansha Palladium Tag\nCompact Multispectrum Energized Membrane\nSmall Inductive Compact Remote Capacitor Transmitter x2\n200mm Rolled Tungsten Compact Plates x14\nN-JM Compact Omnidirectional Tracking Enhancer x5\nMultifrequency S\n100MN Monopropellant Enduring Afterburner x20\nTa3 Compact Ship Scanner x13\nHeavy Gremlin Compact Energy Neutralizer x3\nConductive Polymer x194\nMicrowave M x7\nInduced Compact Multispectral ECM x3\nFleeting Compact Stasis Webifier x5\nExperimental Energized Thermal Membrane I x2\nSerpentis Diamond Tag x14\nInitiated Compact Warp Scrambler x8\nSmall Focused Modal Pulse Laser I\nMedium Solace Scoped Remote Armor Repairer x4\nPL-0 Scoped Cargo Scanner x6\nUranium Charge S x600\nSmall 'Hope' Hull Reconstructor I x2\nSmall I-a Enduring Armor Repairer x3\nSmall Knave Scoped Energy Nosferatu x13\nTachyon Anode Particle Stream I x2\nUpgraded Armor EM Hardener I x8\nAlumel-Wired Enduring Sensor Booster x7\nInfrared M x7\nLinked Enduring Remote Sensor Booster x3\nCharred Micro Circuit x572\nConductive Thermoplastic\nType-E Enduring Cargo Scanner x13\nHeavy Water x37806\nMark I Compact Capacitor Flux Coil x11\n5MN Quad LiF Restrained Microwarpdrive x3\nPlutonium Charge S x200\nHeavy Brief Capacitor Overcharge I x13\nMelted Capacitor Console x62\nModal Light Neutron Particle Accelerator I x2\nPrototype Thermal Plating I x2\nRadio S x5\nLarge I-a Enduring Armor Repairer x32\n1600mm Rolled Tungsten Compact Plates x11\nHobgoblin I x7\nParticle Bore Compact Mining Laser x12\nM51 Benefactor Compact Shield Recharger x2\nSmall I-ax Enduring Remote Armor Repairer x7\n100mm Crystalline Carbonide Restrained Plates x6\nAntimatter Charge S x400\nLarge Coaxial Compact Remote Armor Repairer x13\nKapteyn Compact Sensor Dampener x4\nXray L x4\nTungsten Charge M x800\nSmall I-b Polarized Structural Regenerator x6\nExperimental Enduring Thermal Armor Hardener I x3\nBaker Nunn Enduring Tracking Disruptor I x4\nExtruded Compact Heat Sink x2\nSmall 'Notos' Explosive Charge I x2\nExperimental Energized Explosive Membrane I x5\nPhased Muon Scoped Sensor Dampener x4\nJ5b Enduring Warp Scrambler x10\nMedium 'Hope' Hull Reconstructor I x2\nMedium Radiative Scoped Remote Capacitor Transmitter x5\nReactive Armor Hardener\nMega Afocal Maser I x3\nPitfall Compact Warp Disruption Field Generator x10\nMedium Knave Scoped Energy Nosferatu x2\nUpgraded EM Coating I\nGamma L x8\nIFFA Compact Damage Control x5\nIridium Charge M x900\nMobile Tractor Unit\nMobile Tractor Unit\nMark I Compact Reinforced Bulkheads x4\nMedium YF-12a Smartbomb x2\nLimited Layered Plating I x2\nUltraviolet S x3\nLead Charge L x17\nLarge Automated Structural Restoration x11\nSmall S95a Scoped Remote Shield Booster\nBlood Palladium Tag\nSerpentis Platinum Tag\nCompact Explosive Energized Membrane x2\nHeavy Anode Pulse Particle Stream I x4\nIron Charge S x700\nBlood Silver Tag\nModal Ion Particle Accelerator I x2\n250mm Carbide Railgun I\nInitiated Enduring Multispectral ECM x3\n800mm Crystalline Carbonide Restrained Plates x16\nDual Afocal Heavy Maser I x2\nVortex Compact Magnetic Field Stabilizer x4\nLimited Energized Thermal Membrane I\nFaint Epsilon Scoped Warp Scrambler x10\nTritanium x5016751\nPraetor I x30\nMedium I-b Polarized Structural Regenerator x5\nExperimental Enduring EM Armor Hardener I x8\nGamma M x8\nMedium Brief Capacitor Overcharge I x8\nDeluge Enduring Burst Jammer x6\nUpgraded Armor Kinetic Hardener I x10\nPrototype Compact Kinetic Armor Hardener I x9\nCompact Kinetic Energized Membrane\nPrototype Compact Explosive Armor Hardener I x4\nWarrior I\n500MN Cold-Gas Enduring Microwarpdrive x20\nTachyon Modulated Energy Beam I\nLarge Rudimentary Concussion Bomb I x6\nDual Heavy Modal Pulse Laser I\nMultifrequency M x4\nHeavy Tapered Capacitor Infusion I x12\nHammerhead I x33\nRegulated Light Neutron Phase Cannon I x2\nUpgraded Multispectrum Coating I\nLarge ACM Compact Armor Repairer x24\nHalting Compact Ladar ECM x3\nLimited Explosive Plating I x2\nMetal Scraps x798\n10MN Y-S8 Compact Afterburner x9\nThorium Charge S x700\nBZ-5 Scoped Gravimetric ECM x2\nLarge Solace Scoped Remote Armor Repairer x18\nRegulated Ion Phase Cannon I\n1MN Y-S8 Compact Afterburner x6\nBlood Diamond Tag x2\nUranium Charge M x11\nDual Anode Heavy Particle Stream I\nEutectic Compact Cap Recharger x21\nCoadjunct Scoped Remote Sensor Booster x6\nUpgraded Armor Explosive Hardener I x12\nLFT Enduring Sensor Dampener x7\nUpgraded Energized Adaptive Nano Membrane I x3\nSmall Focused Afocal Maser I x2\nHeavy Modal Pulse Laser I x5\n425mm 'Scout' Accelerator Cannon x12\nMedium Tapered Capacitor Infusion I\n5MN Y-T8 Compact Microwarpdrive x5\nLimited Armor Thermal Hardener I x9\nAML Compact Omnidirectional Tracking Link x8\nSmall Rudimentary Concussion Bomb I x3\n100MN Y-S8 Compact Afterburner x22\nLimited Energized Explosive Membrane I\nTangled Power Conduit x85\nRegulated Mega Neutron Phase Cannon I x11\nContaminated Nanite Compound x330\nSmall Shield Extender I x2\nDual Heavy Modulated Pulse Energy Beam I\nPlutonium Charge M x11\nDefective Current Pump x102\n'Grail' Layered Plating I\nRadio M x9\nMega Modal Laser I x2\nReinforced Metal Scraps\nMedium I-ax Enduring Remote Armor Repairer x8\nUltraviolet L x3\nTripped Power Circuit x570\n200mm Crystalline Carbonide Restrained Plates x15\nAntimatter Charge M x700\nLimited Mega Neutron Blaster I x10\nHornet I x3\nMedium 'Vehemence' Shockwave Charge x3\nSmall Murky Compact Remote Shield Booster\nTungsten Charge L x13\nLarge 'Hope' Hull Reconstructor I x18\nHeavy F-RX Prototype Capacitor Boost x14\nCalm Firestorm Filament\nPower Circuit\nCompact Thermal Energized Membrane x2\nMedium C5-L Compact Shield Booster\nHeavy Modulated Pulse Energy Beam I\n150mm Compressed Coil Gun I\nHeavy Ghoul Compact Energy Nosferatu x5\nDual Modal Heavy Laser I x3\nCetus Scoped Burst Jammer x5\nUpgraded Thermal Coating I x4\nIridium Charge L x15\nF-12 Enduring Tracking Computer x5\nLimited Neutron Blaster I x2\nLarge YF-12a Smartbomb x5\nLimited Armor EM Hardener I x7\nMedium Infectious Scoped Energy Neutralizer\nHeavy Afocal Maser I x3\nUltraviolet M x8\n'Element' Kinetic Plating I\nF-89 Compact Signal Amplifier x8\nLarge Inductive Compact Remote Capacitor Transmitter x10\nSerpentis Electrum Tag\nMedium 'Notos' Explosive Charge I x2\n'Collateral' Adaptive Nano Plating I\nMark I Compact Reactor Control Unit x5\nType-D Restrained Capacitor Flux Coil x3\nMedium I-a Enduring Armor Repairer x7\n50MN Quad LiF Restrained Microwarpdrive x14\nIron Charge M x12\nHeavy F-RX Compact Capacitor Booster x11\n400mm Rolled Tungsten Compact Plates x17\nType-D Restrained Reinforced Bulkheads x4\nMark I Compact Power Diagnostic System x7\nDDO Scoped Tracking Disruptor I x4\n10MN Monopropellant Enduring Afterburner x6\n1600mm Crystalline Carbonide Restrained Plates x16\nFZ-3a Enduring Gravimetric ECM x6\nSmall Coaxial Compact Remote Armor Repairer\nCZ-4 Compact Gravimetric ECM x7\nExperimental Enduring Explosive Armor Hardener I x11\nLarge Compact Pb-Acid Cap Battery x20\nMedium Rudimentary Concussion Bomb I x7\nExperimental Energized Adaptive Nano Membrane I x2\nInitiated Compact Warp Disruptor x9\nPrototype Compact Thermal Armor Hardener I x11\n500MN Y-T8 Compact Microwarpdrive x15\nJ5 Enduring Warp Disruptor x15\nLimited Light Ion Blaster I x2\nSmall Focused Modal Laser I\nEP-S Gaussian Scoped Mining Laser x14\n5MN Cold-Gas Enduring Microwarpdrive x7\nBroken Drone Transceiver x210\n'Excavator' Ice Harvesting Drone\n'Excavator' Ice Harvesting Drone x4\nUpgraded Kinetic Coating I x3\n500MN Quad LiF Restrained Microwarpdrive x13\nMega Modulated Energy Beam I\nSmall Compact Pb-Acid Cap Battery x3\nSmall YF-12a Smartbomb x3\nLimited EM Plating I x2\nSalvager II x16\nThorium Charge M x12\nFederation Navy Ogre\nLead Charge S x200\nAnode Mega Neutron Particle Cannon I x8\nUranium Charge L x16\nLarge I-b Polarized Structural Regenerator x16\nSmall Brief Capacitor Overcharge I x5\n250mm Prototype Gauss Gun\nBlood Gold Tag\nDamaged Artificial Neural Network x223\nBlood Brass Tag x4\nHeavy Karelin Scoped Stasis Grappler x16\nSmall Ghoul Compact Energy Nosferatu x10\nLanguid Enduring Ladar ECM x2\nMark I Compact Capacitor Power Relay x8\nUpgraded Energized Kinetic Membrane I x4\nM-36 Enduring Warp Disruption Field Generator\nLarge 'Vehemence' Shockwave Charge x2\nLimited Energized EM Membrane I x3\nMultifrequency L\nDual Modulated Heavy Energy Beam I\nExperimental Thermal Plating I x4\nF-23 Compact Remote Sensor Booster x3\n150mm Carbide Railgun I\nPlutonium Charge L x19\nSalvager I\nXray M x5\nPrototype Compact EM Armor Hardener I x14\nHeavy Anode Particle Stream I\nRadio L x11\nMega Anode Particle Stream I x3\n100mm Rolled Tungsten Compact Plates x8\n425mm Prototype Gauss Gun x3\nRash Compact Burst Jammer x4\nLarge I-ax Enduring Remote Armor Repairer x12\nStandard L x5\nAntimatter Charge L x13\nSmall Automated Structural Restoration x4\nSmall Infectious Scoped Energy Neutralizer\nAE-K Compact Drone Damage Amplifier x6\nMedium ACM Compact Armor Repairer x10\nMicrowave S x4\nMedium Murky Compact Remote Shield Booster\nSmall ACM Compact Armor Repairer x6\nExperimental Energized Armor Layering Membrane I\nLarge 'Notos' Explosive Charge I x8\nFaint Scoped Warp Disruptor x8\nEnfeebling Scoped Ladar ECM x9\nOgre I x22\nSmall Solace Scoped Remote Armor Repairer x2\nArmor Plates x290\nModal Mega Neutron Particle Accelerator I x5\nMedium Ghoul Compact Energy Nosferatu x5\nBalmer Series Compact Tracking Disruptor I x6\nML-3 Scoped Survey Scanner x13\n1MN Monopropellant Enduring Afterburner x2\nSmall Radiative Scoped Remote Capacitor Transmitter x9\nUpgraded Layered Coating I x2\n425mm Compressed Coil Gun I x8\nInfrared S\nContaminated Lorentz Fluid x534\nLimited Armor Explosive Hardener I x10\nHeavy Infectious Scoped Energy Neutralizer x9\nLimited Energized Adaptive Nano Membrane I\nType-D Restrained Expanded Cargo x2\n425mm Carbide Railgun I x11\nStandard M x6\n50MN Cold-Gas Enduring Microwarpdrive x17\nMedium Inefficient Hull Repair Unit\nMedium Inductive Compact Remote Capacitor Transmitter x9\n50MN Y-T8 Compact Microwarpdrive x7\nExperimental Kinetic Plating I\nTachyon Modal Laser I x3\nSerpentis Palladium Tag x3\nAgency 'Hardshell' TB3 Dose I\n250mm 'Scout' Accelerator Cannon x3\nBurned Logic Circuit x674\n'Spiegel' EM Plating I\nHeavy Gunnar Compact Stasis Grappler x16\nIron Charge L x23\n800mm Rolled Tungsten Compact Plates x8\nF-293 Scoped Remote Tracking Computer x8\nModal Neutron Particle Accelerator I x3\nHeavy Jigoro Enduring Stasis Grappler x13\nHeavy Modal Laser I x2\nMedium Automated Structural Restoration x7\nLimited Armor Kinetic Hardener I x15\nHighstroke Scoped Guidance Disruptor x3\nMedium Coaxial Compact Remote Armor Repairer x12\nTungsten Charge S\nMedium F-RX Prototype Capacitor Boost x2\nExperimental Enduring Kinetic Armor Hardener I x8\nExperimental Energized Kinetic Membrane I x2\nC-IR Compact Guidance Disruptor x5\nFried Interface Circuit x455\nCompact EM Energized Membrane x5\nLarge Radiative Scoped Remote Capacitor Transmitter x7\nLimited Light Neutron Blaster I x2\nA-211 Enduring Guidance Disruptor x4\nHeavy Knave Scoped Energy Nosferatu x10\nUpgraded Explosive Coating I\nSmall Ancillary Armor Repairer\nIridium Charge S x900\nF-90 Compact Sensor Booster x5\nX5 Enduring Stasis Webifier x12\nLimited Ion Blaster I x2\nLimited Thermal Plating I\nThorium Charge L x15\nBlood Crystal Tag\nLead Charge M x13\nBerserker I x50\nHeavy Modulated Energy Beam I x4\nOxygen Isotopes x162886\nHeavy Water x764\nLiquid Ozone x10753\nCompressed Monoclinic Bistot x107\nCompressed Prismatic Gneiss x20\nCompressed Crystalline Crokite x240\nCompressed Enriched Clear Icicle x584\nCompressed Gleaming Spodumain x209\nCompressed Prime Arkonor x26\nCompressed Vitreous Mercoxit x20\nCompressed Obsidian Ochre x645\nMobile Tractor Unit\nMagnetometric Sensor Cluster Blueprint\nMining Laser Optimization Charge x37968\nPraetor II x30\nArkonor Mining Crystal II x8\nOscillator Capacitor Unit Blueprint\nVeldspar Mining Crystal II x5\nModulated Deep Core Strip Miner II x5\nNavy Cap Booster 3200 x77\nInfiltrator I x2\nCompact EM Shield Hardener x3\nIce Harvesting Drone II x13\nDamage Control II\nLiquid Ozone x69852\nCrystalline Carbonide Armor Plate Blueprint\nExpired Crimson Cerebral Accelerator x2\nInertial Stabilizers II x3\nMining Equipment Preservation Charge x37176\nMining Drone II x8\nFusion Reactor Unit Blueprint\nHobgoblin II x6\nModulated Strip Miner II x4\nIce Harvester II\nPhoton Microprocessor Blueprint\nReinforced Bulkheads II x3\nTengu Defensive - Covert Reconfiguration x2\nProcurer Blueprint (Copy) x8\nProcurer Blueprint (Copy) x2\nPulse Shield Emitter Blueprint\nIce Harvester Upgrade II\nMining Laser Upgrade II x7\nCovert Ops Cloaking Device II\nCrokite Mining Crystal II x9\nMining Laser Field Enhancement Charge x37535\nBistot Mining Crystal II x4\nCapital Remote Shield Booster II\nSyndicate Damage Control\nSpodumain Mining Crystal II x16\nMultispectrum Shield Hardener II\nScordite Mining Crystal II x6\nOmnidirectional Tracking Enhancer II x2\n'Wetu' Mobile Depot\nProcurer Blueprint\nIon Thruster Blueprint	funny dump of modules: https://zkillboard.com/kill/82154154/
5	t	5	[Tristan, Tristan (убивает в клозе, Tabord)]\nDamage Control II\nMultispectrum Energized Membrane II\nSmall Ancillary Armor Repairer\n\nWarp Scrambler II\n1MN Monopropellant Enduring Afterburner\nSmall F-RX Compact Capacitor Booster\n\nSmall Unstable Power Fluctuator I\nSmall Unstable Power Fluctuator I\nSmall Unstable Power Fluctuator I\n\nSmall Egress Port Maximizer I\nSmall Egress Port Maximizer I\nSmall Ancillary Current Router I\n\n\n\nHobgoblin II x8\n\nNanite Repair Paste x32\nNavy Cap Booster 200 x12\n\n\n	хитрый фит Tabord Ormand'а для клозового Tristan-а
\.