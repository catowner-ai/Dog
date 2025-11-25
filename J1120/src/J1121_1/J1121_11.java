package J1121_1;

public class J1121_11 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		        // 方法1：直接按照規律迴圈累加（推薦，最清晰）
		        int sum = 0;
		        int num = 4;
		        boolean add5 = true;  // 第一步加5
		        
		        while (num <= 99) {
		            sum += num;
		            if (add5) {
		                num += 5;
		            } else {
		                num += 4;
		            }
		            add5 = !add5;  // 切換
		        }
		        
		        System.out.println("總和 = " + sum);  // 輸出 1133
		        
		        // ----------------------------------------------------
		        // 方法2：用兩組等差數列分別計算（更快）
		        // 奇數項：4, 13, 22, ..., 99   (首項4，公差9)
		        // 偶數項：9, 18, ..., 94       (首項9，公差9)
	
		                // 奇數位置：4, 13,g 22, ..., 99  → 首項4，末項99，公差9，共10項
		                int n = 10;
		                int sum1 = n * (4 + 99) / 2;        // 515

		                // 偶數位置：9, 18, 27, ..., 94  → 首項9，末項94，公差9，共10項
		                int sum2 = n * (9 + 94) / 2;        // 618

		                System.out.println("總和 = " + (sum1 + sum2));  // 1133
		            }
		        }        
		
	


