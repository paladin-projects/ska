PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "self_assessment_hardware" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" text NOT NULL UNIQUE);
INSERT INTO self_assessment_hardware (product) VALUES
('ProLiant & Apollo'),
('BladeSystem'),
('Synergy'),
('SimpliVity'),
('B-series SAN'),
('Aruba Switches'),
('Aruba Routers'),
('FlexNetwork Switches'),
('FlexFabric Switches'),
('OfficeConnect Switches'),
('Aruba Mobility Controllers'),
('Aruba Hotspots'),
('MSA'),
('Nimble'),
('3PAR/Primera'),
('Autoloader & MSL'),
('StoreOnce'),
('StoreEasy')
ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS "self_assessment_taskhw" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "task" text NOT NULL UNIQUE);
INSERT INTO self_assessment_taskhw (task) VALUES
('Product Line'), 
('Part Replacement'), 
('Rack Mounting'), 
('Cabling'), 
('Startup'), 
('Basic Configuration'), 
('Log Collection'), 
('Log Parsing'), 
('Diagnostics'), 
('Configuration Design'), 
('Firmware Update'), 
('Performance Metrics Setup'), 
('Performance Collection')
ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS "self_assessment_software" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "product" text NOT NULL UNIQUE);
INSERT INTO self_assessment_software (product) VALUES
('Microsoft Windows Server'),
('Red Hat Enterprise Linux'),
('SUSE Linux Enterprise Server'),
('VMware vSphere'),
('Microsoft Hyper-V'),
('Red Hat Enterprise Virtualization'),
('SUSE Xen Virtualization'),
('SUSE KVM Virtualization'),
('Docker'),
('Kubernetes'),
('Microsoft Failover Cluster'),
('Red Hat High Availability Add-On'),
('SUSE Linux Enterprise High Availability Extension'),
('Microfocus Data Protector'),
('Veeam Backup & Replication'),
('DellEMC NetWorker'),
('Veritas NetBackup'),
('Veritas Backup Exec'),
('Microsoft SQL Server'),
('Oracle Database'),
('PostgreSQL'),
('MySQL/MariaDB')
ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS "self_assessment_tasksw" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "task" text NOT NULL UNIQUE);
INSERT INTO self_assessment_tasksw (task) VALUES
('Product'), 
('Installation'), 
('Basic Configuration'), 
('Fine Tuning'), 
('Performance Collection'), 
('Performance Tuning')
ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS "self_assessment_processes" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "process" text NOT NULL UNIQUE);
INSERT INTO self_assessment_processes (process) VALUES
('PRINCE2 Project Management'),
('PMI Project Management'),
('TOGAF Enterprise Architecture'),
('Technical Writing'),
('Negotiations with Customer'),
('Correspondence with Customer'),
('Performance Analysis (Statistics)'),
('Solution High Level Design'),
('Solution Low Level Design'),
('Customer Presentations'),
('Testing and Acceptance Planning'),
('Technical Training Delivery'),
('Technical Training Development'),
('ITIL/ITSM')
ON CONFLICT DO NOTHING;
CREATE TABLE IF NOT EXISTS "self_assessment_levels" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "weight" integer NOT NULL UNIQUE, "level" text NOT NULL UNIQUE, "description" text NOT NULL UNIQUE);
INSERT OR REPLACE INTO "self_assessment_levels" ("weight","level","description") VALUES
(0,'— Select your level —','A value indicating that there is no level selected for this field'),
(1,'None','Have no knowledge on product, technology or process'),
(2,'Basic','Have general knowledge on product, technology or process; can follow prepared instructions'),
(3,'Middle','Have experience with product, technology or process; can find instructions and follow them'),
(4,'Professional','Navigate freely in product, technology or process; can provide instructions and advise to customer'),
(5,'Expert','Know all quircks of product, technology or process; can provide instructions, advise to customer and deliver trainings');
COMMIT;
