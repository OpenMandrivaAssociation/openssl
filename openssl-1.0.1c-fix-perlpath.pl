--- openssl-1.0.1c/util/perlpath.pl~	1999-03-10 20:57:05.000000000 +0100
+++ openssl-1.0.1c/util/perlpath.pl	2012-12-28 15:31:20.357657353 +0100
@@ -1,13 +1,13 @@
-#!/usr/local/bin/perl
+#!/usr/bin/perl
 #
 # modify the '#!/usr/local/bin/perl'
 # line in all scripts that rely on perl.
 #
 
-require "find.pl";
+use File::Find;
 
 $#ARGV == 0 || print STDERR "usage: perlpath newpath  (eg /usr/bin)\n";
-&find(".");
+find(\&wanted, ".");
 
 sub wanted
 	{
