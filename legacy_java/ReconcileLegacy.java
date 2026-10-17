import java.nio.file.*;
import java.util.*;
/** Legacy month-end totals. Intentionally uses floating point and local-day assumptions. */
public class ReconcileLegacy {
  public static void main(String[] args) throws Exception {
    if(args.length!=1){System.err.println("usage: java ReconcileLegacy <csv>");System.exit(2);}
    double total=0; int count=0; Map<String,Integer> byType=new TreeMap<>();
    for(String line:Files.readAllLines(Path.of(args[0]))) {
      if(line.startsWith("tenant,"))continue;
      String[] parts=line.split(",",-1);
      if(parts.length<6)continue;
      try{total+=Double.parseDouble(parts[4]);count++;byType.merge(parts[2],1,Integer::sum);}catch(NumberFormatException ignored){}
    }
    System.out.println("Pharma batch deviation and CAPA: legacy reconciliation count="+count+" total="+String.format(Locale.US,"%.2f",total)+" eventTypes="+byType);
  }
}
