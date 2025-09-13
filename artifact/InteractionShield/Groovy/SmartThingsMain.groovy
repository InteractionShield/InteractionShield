import groovy.console.ui.ScriptToTreeNodeAdapter
import groovy.console.ui.SwingTreeNodeMaker
import groovy.json.JsonOutput
import org.codehaus.groovy.control.CompilerConfiguration

import javax.swing.tree.DefaultMutableTreeNode
import groovy.cli.commons.CliBuilder
import java.nio.file.Paths

class SmartThingsMain {
    static int phaseInt = 3 //CONVERSION
    static SwingTreeNodeMaker swingTreeNodeMaker = new SwingTreeNodeMaker()
    static GroovyClassLoader groovyClassLoader = new GroovyClassLoader()
    static CompilerConfiguration compilerConfig = null
    static boolean showScriptFreeFormBool = true
    static boolean showScriptClassBool = false
    static boolean showClosureClassesBool = false
    static ScriptToTreeNodeAdapter scriptToTreeNodeAdapter = new ScriptToTreeNodeAdapter(groovyClassLoader, showScriptFreeFormBool, showScriptClassBool, showClosureClassesBool, swingTreeNodeMaker, compilerConfig)

    static String projectResultsStr = ""
    static String datasetDirStr = ""

    static void main(String[] args) throws IOException {

        def cli = new CliBuilder(usage: 'groovy SmartThingsMain.groovy [options]')
        cli.with {
            d(longOpt: 'dataset', args: 1, argName: 'DIR', 'Use Datasets from a directory')
            r(longOpt: 'result',  args: 1, argName: 'DIR', 'Result output directory')
        }

        def opts = cli.parse(args)
        if (!opts) return

        if (opts.d) datasetDirStr = opts.d
        if (opts.r) projectResultsStr = opts.r


        String resultInformationFileStr = "${projectResultsStr}/SmartThings.json"

        List<File> filesList = new File(datasetDirStr).listFiles().sort { it.name }
        int numFilesInt = filesList.size()

        FileWriter fileWriter = new FileWriter(resultInformationFileStr)
        BufferedWriter bufferedWriter = new BufferedWriter(fileWriter)

        long beginTimeLong = System.currentTimeMillis()

        bufferedWriter.write("{\n")

        for (int iInt = 0; iInt < numFilesInt; iInt++) {
            File appFile = filesList[iInt]
            String fileNameStr = appFile.getName()

//            if(fileNameStr!="ecobeeChangeMode[natalan@SmartThings].groovy"){
//                continue
//            }

            println("${iInt+1}. ${fileNameStr}")

            try {
                DefaultMutableTreeNode rootDmtn = scriptToTreeNodeAdapter.compile(appFile.text, phaseInt)
                SmartThingsHelper smartThingsHelper = new SmartThingsHelper(rootDmtn)
                rootDmtn.getFirstChild().getPropertyValue("text")

                Map InformationMap = smartThingsHelper.getInformation()

                String InformationJsonStr = JsonOutput.toJson(InformationMap)
                String InformationPrettyJsonStr = JsonOutput.prettyPrint(InformationJsonStr)
                bufferedWriter.write("\"${fileNameStr}\":")
                bufferedWriter.write(InformationPrettyJsonStr)
                if (iInt == numFilesInt - 1) {
                    bufferedWriter.write("\n")
                } else {
                    bufferedWriter.write(",\n")
                }
                bufferedWriter.flush()
            }
            catch (Exception e) {
                println("Exception -> ${fileNameStr}")
//                File newFile = new File("${exceptionAppDirStr}/${fileNameStr}")
//                newFile << appFile.text
            }

//            break
        }
        bufferedWriter.write("}\n")
        bufferedWriter.close()

        long endTimeLong = System.currentTimeMillis()
        long totalSecsLong = (endTimeLong - beginTimeLong) / 1000

        long hoursLong = totalSecsLong / 3600;
        long minutesLong = (totalSecsLong % 3600) / 60;
        long secondsLong = totalSecsLong % 60;

        // println("Time cost: ${hoursLong} Hours, ${minutesLong} Minutes, ${secondsLong} Seconds.")
    }
}
