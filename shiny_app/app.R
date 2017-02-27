library(data.table)
library(shiny)
library(shinydashboard)
library(plotly)
# library(made4)

# load data
load("mRNA_datasets.RData")
load("lncRNA_datasets.RData")
load("mRNA_name_label.RData")
colnames(name_label_mRNA) <- c("label", "title")

# Define search index
searchRowName <- "gene_symbol"
setkeyv(mRNA_datasets, searchRowName)
setkeyv(lncRNA_datasets, searchRowName)

### Debug codes
# test_gene <- "GAPDH"
# test_list <- mRNA_datasets[test_gene]
# test_list <- mRNA_datasets[c("GAPDH", "PUM1")]
# write.table(data.frame(title=colnames(test_list)),quote = F, file = "title_name.txt", sep="\t")

# Filtering data table prep
data_filtering <- function(test_list){
  gene_name <- test_list[[3]]
  ref_id <- test_list[[2]]
  data_list <- test_list[,4:length(test_list[1,]), with = F]
  
  # Remove NA columns
  data_list <- data_list[, colSums(is.na(data_list)) == 0, with = F]
  
  # all samples
  data_list <- data.table(value=as.numeric(t(data_list)), label=as.factor(colnames(data_list)), key="value")
  data_list <- merge(data_list, name_label_mRNA, "label")
  data_list <- data.table(data_list, key="value")
  data_list$title <- factor(data_list$title, level=data_list$title)
  
  return(data_list)
}

# Select top20 data table
top_data_selection <- function(data_list){
  fig_data <- ""
  if(length(data_list[[1]]) >= 40){
    data_list_down <- data_list[1:20,]
    data_list_up <- data_list[(length(data_list[[1]])-19):length(data_list[[1]]),]
    fig_data <- rbind(data_list_down, data_list_up)
  }else{
    fig_data <- data_list
  }
  
  fig_data$title <- factor(fig_data$title, level=fig_data$title)
  
  return(fig_data)
}

plot_table <- function(test_list ,title_name){
  # Filtering
  data_list <- data_filtering(test_list)
  
  # Sort Fold-change
  new_list <- data.table(Stimulation=data_list$title, Fold_change=data_list$value, key="Fold_change")
  
  return(new_list)
}


plotly_bar_chart <- function(test_list ,title_name, filtering){
  # Filtering
  data_list <- data_filtering(test_list)
  
  # Extract 20 up/down samples
  fig_data <- top_data_selection(data_list)
  
  if(filtering == "2"){
    m <- list(
      l = 650,
      r = 50,
      b = 50,
      t = 50,
      pad = 4
    )
    
    p_all <- plot_ly(data_list,
                     x = ~value,
                     y = ~title,
                     type = "bar",
                     orientation = 'h') %>% 
      layout(title = title_name,
             xaxis = list(title = "Log2(Treated/Control)"),
             yaxis = list(title = "", tickfont = 9),
             margin = m)
    return(p_all)
  }
  
  
  m <- list(
    l = 650,
    r = 50,
    b = 50,
    t = 50,
    pad = 4
  )
  
  p <- plot_ly(fig_data,
               x = ~value,
               y = ~title,
               type = "bar",
               orientation = 'h') %>% 
    layout(title = title_name,
           xaxis = list(title = "Log2(Treated/Control)"),
           yaxis = list(title = "", tickfont = 9),
           margin = m)
  return(p)
}

# test_gene <- "GAPDH"
# main_list <- mRNA_datasets[test_gene]
# sample_names <- c("PUM2","GAPDH", "PUM1")
# target_list <- mRNA_datasets[sample_names]
# sample_number <- 3
# plotting heatmap
# plotly_heatmap <- function(target_list, main_list, sample_names, sample_number){
#   target_list2 <- target_list[,4:length(target_list[1,]), with = F]
#   main_list2 <- main_list[,4:length(main_list[1,]), with = F]
# 
#   # Remove NA columns
#   target_list2 <- target_list2[, colSums(is.na(target_list2)) == 0, with = F]
#   main_list2 <- main_list2[, colSums(is.na(main_list2)) == 0, with = F]
#   
#   # all samples
#   target_list2 <- data.table(value=t(target_list2), label=as.factor(colnames(target_list2)))
#   main_list2 <- data.table(value=as.numeric(t(main_list2)), label=as.factor(colnames(main_list2)))
#   main_list2 <- merge(main_list2, name_label_mRNA, "label")
#   main_list2 <- data.table(main_list2, key="value")
#   main_list2$title <- factor(main_list2$title, level=main_list2$title)
#   main_list2 <- top_data_selection(main_list2)
#   
#   data_list3 <-  merge(main_list2, target_list2, "label")
#   data_list3 <- data.table(data_list3, key="value")
#   fig_data <- data.table(t(data_list3[,4:(sample_number+3),with=F]))
#   label_data <- as.vector(data_list3$title)
#   # colnames(fig_data) <- label_data
#   # rownames(fig_data) <- sample_names
#   
#   m <- list(
#     l = 100,
#     r = 50,
#     b = 650,
#     t = 50,
#     pad = 4
#   )
#   p <- plot_ly(x = label_data, y = as.factor(sample_names), z = as.matrix(fig_data), type = "heatmap") %>%
#               layout(margin = m)
#   return(p)
# }

# UI - shiny dashboard
ui_body <- dashboardBody(
  # tabItems(
    # Bar Chart
    tabItem(tabName = "BarChart",
            fluidRow(
              box(title = tagList(icon("check-square"), "Inputs"), status = "primary", solidHeader = TRUE, width = 2, # background = "navy",
                  # mRNA / lncRNA selection
                  radioButtons("radio", label = "Select Gene Type",
                               choices = list("mRNA" = 1, "lncRNA" = 2),
                               selected = 1),
                  
                  # mRNA / lncRNA selection
                  radioButtons("radio2", label = "Bar chart(Fold-change)",
                               choices = list("Top20" = 1, "ALL" = 2),
                               selected = 1),
                  
                  # text input
                  textInput("text",
                            label = "Input your favorite gene symbol",
                            placeholder = "Search..."),
                  
                  # Submit
                  submitButton(tagList(icon("search"), "Update View")),
                  
                  # Download
                  hr(),
                  tags$b("Data Download"),
                  tags$h5(""),
                  downloadButton('downloadData', 'Download')
              ),
              
              box(title = tagList(icon("bar-chart"), "log2(Fold-change)"), status = "primary", solidHeader = TRUE, width = 10,
                  plotlyOutput("plot1",
                               width = 1150, height = 800)
              )
            ),
            
            fluidRow(
              box(title = tagList(icon("th-list"), "RNA-seq data list"), status = "primary", solidHeader = TRUE, width = 12,
                  DT::dataTableOutput("table")
                  # verbatimTextOutput('table_selected')
              )
            )
    )
    # ),
    # HeatMap
    # tabItem(tabName = "Heatmap",
    #         fluidRow(
    #           box(title = tagList(icon("check-square"), "Inputs"), status = "primary", solidHeader = TRUE, width = 2,
    #               # text input
    #               textInput("text_heatmap",
    #                         label = "Input a space-delimited target gene list",
    #                         placeholder = "Search..."),
    #               
    #               # Submit
    #               submitButton(tagList(icon("search"), "Update View"))
    #           ),
    #           box(title = tagList(icon("bar-chart"), "log2(Fold-change)"), status = "primary", solidHeader = TRUE, width = 10,
    #               plotlyOutput("heatmap",
    #                            width = 600, height = 1150)
    #           )
    #         )
    # )
  # )
)

ui_sidebar <- dashboardSidebar(disable = TRUE)
  # sidebarMenu(
  #   menuItem("BarChart", tabName = "BarChart", icon = icon("bar-chart")),
    # menuItem("Heatmap", tabName = "Heatmap", icon = icon("th"))
#   )
# )


ui <- dashboardPage(
  dashboardHeader(title = "RNA-seq Collection"),
  ui_sidebar,
  ui_body
)

# Server- define server logic required to draw RNA decay curve
server <- shinyServer(function(input, output){
  # Draw bar chart
  output$plot1 <- renderPlotly({
    if(input$radio == "1"){
      test_list <- mRNA_datasets[input$text]
      plotly_bar_chart(test_list, input$text, input$radio2)

    }else if(input$radio == "2"){
      test_list <- lncRNA_datasets[input$text]
      plotly_bar_chart(test_list, input$text, input$radio2)
    }
  })
  
  # Filter data based on selections
  dataset <- reactive({
    if(input$radio == "1"){
      test_list <- mRNA_datasets[input$text]
      plot_table(test_list, input$text)
    }else if(input$radio == "2"){
      test_list <- lncRNA_datasets[input$text]
      plot_table(test_list, input$text)
    }
  })
  
  output$table <- DT::renderDataTable(
    dataset()
  )
  
  # output$table_selected <- renderPrint({
  #   s = input$table_rows_selected
  #   cat('These rows were selected:\n\n')
  #   if (length(s)) {
  #     cat(s, sep = ', ')
  #   }
  # })

  # Data Download
  output$downloadData <- downloadHandler(
    filename = function() {
      paste(input$text, '.csv', sep='')
    },
    content = function(file) {
      write.csv(dataset(), file)
    }
  )
  
  # HeatMap
  # output$heatmap <- renderPlotly({
  #   gene_names <- strsplit(input$text_heatmap, " ")[[1]]
  #   target_number <- length(gene_names)
  #   if(input$radio == "1"){
  #     main_list <- mRNA_datasets[input$text]
  #     target_list <- mRNA_datasets[gene_names]
  #     plotly_heatmap(target_list, main_list, gene_names, target_number)
  #     
  #   }else if(input$radio == "2"){
  #     main_list <- lncRNA_datasets[input$text]
  #     target_list <- lncRNA_datasets[gene_names]
  #     plotly_heatmap(target_list, main_list, gene_names, target_number)
  #   }
  # })
})

# Run the application
shinyApp(ui = ui, server = server)



