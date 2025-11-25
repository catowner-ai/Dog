package J1124;

public class J1124_11 {

	public static void main(String[] args) {
		// TODO Auto-generated method stub
		int x[] = {25,10,39,40,33,12};
		int k,times,temp;
		k = x.length-1;
		while(k!=0){ 
		    times = 0;
		    for(int i=0;i<=k-1;i++){
		        if(x[i]>x[i+1]){
		            temp = x[i]; 
		            x[i] = x[i+1]; x[i+1] = temp;
		            times = i;
		        }
		    }
		    k = times;
		}
		for(int num : x)//整數num迭代(逐一依序被設定成陣列x中的元素)6個就執行6次 就不用起始及終止值
		    System.out.print(num+ "\t");
	}

}
